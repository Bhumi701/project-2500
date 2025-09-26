const express = require('express');
const https = require('https');
const url = require('url');
const { initializeApp, cert } = require('firebase-admin/app');
const { getFirestore, FieldValue } = require('firebase-admin/firestore');
const app = express();
const port = 3000;

// --- Firebase Setup ---
try {
    const serviceAccount = require('./serviceAccountKey.json');
    initializeApp({ credential: cert(serviceAccount) });
    console.log("✅ Firebase Admin SDK initialized successfully.");
} catch (error) {
    console.error("\n❌ FATAL ERROR: Could not find or parse 'serviceAccountKey.json'.");
    console.error("Please ensure the file exists and is a valid JSON file from your Firebase project.\n");
    process.exit(1);
}
const db = getFirestore();
console.log("✅ Firebase Firestore connected successfully.");

app.use(express.json({ limit: '10mb' }));
app.use(express.static('.'));

// --- API Keys ---
const GEMINI_API_KEY = "AIzaSyA0JQMrzRv_Gw_Wr_ekGSG73v_Xl5T--SU";

if (!GEMINI_API_KEY) {
    console.warn("\n⚠️ WARNING: GEMINI_API_KEY is not set. The application will not work.\n");
}

const API_BASE_URL = `https://generativelanguage.googleapis.com/v1beta/models/`;
const TEXT_MODEL = "gemini-1.5-flash-latest";

// --- API Call Helpers ---
async function makeApiCall(model, payload) {
    const apiUrl = new url.URL(`${API_BASE_URL}${model}:generateContent?key=${GEMINI_API_KEY}`);
    
    const options = {
        hostname: apiUrl.hostname,
        path: apiUrl.pathname + apiUrl.search,
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    };

    return new Promise((resolve, reject) => {
        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => { data += chunk; });
            res.on('end', () => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    try {
                        resolve(JSON.parse(data));
                    } catch (e) {
                        reject(new Error('Failed to parse JSON response.'));
                    }
                } else {
                    reject(new Error(`API call failed with status ${res.statusCode}`));
                }
            });
        });

        req.on('error', (e) => reject(e));
        req.write(JSON.stringify(payload));
        req.end();
    });
}

async function makeApiCallWithRetry(model, payload, maxRetries = 3) {
    let delay = 1000;
    for (let i = 0; i < maxRetries; i++) {
        try {
            return await makeApiCall(model, payload);
        } catch (error) {
            if (error.message.includes('503') || error.message.includes('UNAVAILABLE')) {
                console.warn(`⚠️ API call failed (attempt ${i + 1}/${maxRetries}), retrying in ${delay/1000}s...`);
                await new Promise(resolve => setTimeout(resolve, delay));
                delay *= 2;
            } else {
                throw error;
            }
        }
    }
    throw new Error(`API call failed after ${maxRetries} attempts.`);
}

// === ROUTES FOR BOTH APPLICATIONS ===

// Serve main pages
app.get('/', (req, res) => {
    res.sendFile(__dirname + '/plant-identifier.html');
});

app.get('/chat', (req, res) => {
    res.sendFile(__dirname + '/agri-assistant.html');
});

// === PLANT IDENTIFIER ENDPOINTS ===

// Plant analysis endpoint
app.post('/api/analyze-plant', async (req, res) => {
    try {
        const { imageBase64, imageMimeType, language } = req.body;
        
        if (!imageBase64 || !imageMimeType) {
            return res.status(400).json({ error: "Image data is required" });
        }

        const languageName = language === 'ml-IN' ? 'Malayalam' : 'English';
        const prompt = `Analyze the image of the plant and provide the output in the following strict format. Respond entirely in ${languageName}. Use these exact labels (translated to the target language) followed by a colon and a space.

Plant Name: [Identified Plant Name]
Condition: [Healthy/Diseased/Pest Infestation]
Disease/Pest Found: [Name of the disease or pest, or "None"]
Suggested Treatment/Care: [Provide a detailed, step-by-step plan for treatment if a disease is found. If the plant is healthy, provide general care tips including watering, sunlight, and soil requirements.]`;

        const payload = { 
            contents: [{ 
                parts: [
                    { text: prompt }, 
                    { inline_data: { mime_type: imageMimeType, data: imageBase64 } }
                ] 
            }] 
        };

        const result = await makeApiCallWithRetry(TEXT_MODEL, payload);
        const analysisText = result.candidates?.[0]?.content?.parts?.[0]?.text;
        
        if (!analysisText) throw new Error("AI returned an empty response");

        res.json({ analysis: analysisText });
    } catch (error) {
        console.error("Plant analysis error:", error);
        res.status(500).json({ error: "Failed to analyze plant image" });
    }
});

// === AGRI-ASSISTANT ENDPOINTS ===

// Chat management endpoints
app.get('/api/chats', async (req, res) => {
    try {
        const { userId } = req.query;
        if (!userId) return res.status(400).json({ error: "User ID is required" });
        
        const chatsRef = db.collection('users').doc(userId).collection('chats');
        const snapshot = await chatsRef.orderBy('createdAt', 'desc').get();
        const chats = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
        res.status(200).json(chats);
    } catch (error) {
        console.error("Error getting chats:", error);
        res.status(500).json({ error: "Failed to retrieve chats" });
    }
});

app.post('/api/chats', async (req, res) => {
    try {
        const { userId, lang, welcomeMessage } = req.body;
        if (!userId || !lang || !welcomeMessage) return res.status(400).json({ error: "Missing required fields" });
        
        const newChatRef = db.collection('users').doc(userId).collection('chats').doc();
        const newChat = {
            id: newChatRef.id,
            title: lang === 'ml-IN' ? 'പുതിയ ചാറ്റ്' : 'New Chat',
            language: lang,
            createdAt: new Date().toISOString(),
            messages: [{ sender: 'ai', text: welcomeMessage }]
        };
        
        await newChatRef.set(newChat);
        res.status(201).json(newChat);
    } catch (error) {
        console.error("Error creating chat:", error);
        res.status(500).json({ error: "Failed to create new chat" });
    }
});

app.post('/api/chats/:chatId/messages', async (req, res) => {
    try {
        const { chatId } = req.params;
        const { userId, prompt } = req.body;
        if (!userId || !prompt) return res.status(400).json({ error: "userId and prompt are required" });

        const chatRef = db.collection('users').doc(userId).collection('chats').doc(chatId);
        await chatRef.update({ messages: FieldValue.arrayUnion({ text: prompt, sender: 'user' }) });

        const currentDoc = await chatRef.get();
        if (!currentDoc.exists) throw new Error("Chat document not found");
        const chatData = currentDoc.data();

        const formattedHistory = chatData.messages.map(msg => ({
            role: msg.sender === 'user' ? 'user' : 'model',
            parts: [{ text: msg.text }]
        }));

        const systemPrompt = `You are 'Agri-Assistant', a specialized AI expert in agriculture. Your sole purpose is to provide information and answer questions related to agriculture. This includes topics like crop cultivation, soil science, pest and disease management, agricultural machinery, farming techniques, government agricultural policies, subsidies, market prices for crops, and sustainable farming practices. You MUST STRICTLY adhere to this domain. If a user asks any question not related to agriculture, you must politely and concisely refuse. Respond in the same language as the user's query.`;

        const payload = {
            contents: formattedHistory,
            systemInstruction: { parts: [{ text: systemPrompt }] }
        };

        const result = await makeApiCallWithRetry(TEXT_MODEL, payload);
        const aiText = result.candidates?.[0]?.content?.parts?.[0]?.text;

        if (!aiText) throw new Error("AI returned an empty response");

        const aiResponse = { text: aiText, sender: 'ai' };
        await chatRef.update({ messages: FieldValue.arrayUnion(aiResponse) });

        // Update chat title if it's still the default
        if (chatData.title === 'New Chat' || chatData.title === 'പുതിയ ചാറ്റ്') {
            const titlePrompt = `Generate a very short title (4-5 words max) for a chat conversation that starts with this user query. Respond with only the title. Query: "${prompt}"`;
            const titlePayload = { contents: [{ parts: [{ text: titlePrompt }] }] };
            const titleResult = await makeApiCallWithRetry(TEXT_MODEL, titlePayload);
            const newTitle = titleResult.candidates?.[0]?.content?.parts?.[0]?.text?.trim().replace(/["'*]/g, "");
            if (newTitle) await chatRef.update({ title: newTitle });
        }

        const updatedChat = (await chatRef.get()).data();
        res.status(200).json({ aiResponse, updatedChat });

    } catch (error) {
        console.error("Error sending message:", error);
        res.status(500).json({ error: "Failed to process message" });
    }
});

app.delete('/api/chats/:chatId', async (req, res) => {
    try {
        const { chatId } = req.params;
        const { userId } = req.query;
        if (!userId) return res.status(400).json({ error: "User ID is required" });
        
        await db.collection('users').doc(userId).collection('chats').doc(chatId).delete();
        res.status(200).json({ success: true });
    } catch (error) {
        console.error("Error deleting chat:", error);
        res.status(500).json({ error: "Failed to delete chat" });
    }
});

app.delete('/api/chats', async (req, res) => {
    try {
        const { userId } = req.query;
        if (!userId) return res.status(400).json({ error: "User ID is required" });
        
        const chatsRef = db.collection('users').doc(userId).collection('chats');
        const snapshot = await chatsRef.get();
        const batch = db.batch();
        snapshot.docs.forEach(doc => batch.delete(doc.ref));
        await batch.commit();
        res.status(200).json({ success: true });
    } catch (error) {
        console.error("Error deleting all chats:", error);
        res.status(500).json({ error: "Failed to delete all chats" });
    }
});

// Recommendations endpoint
app.get('/api/recommendations', async (req, res) => {
    try {
        const { userId } = req.query;
        if (!userId) return res.status(400).json({ error: "User ID is required" });
        
        const chatsRef = db.collection('users').doc(userId).collection('chats');
        const snapshot = await chatsRef.get();
        if (snapshot.empty) return res.status(404).json({ error: "No chat history found" });

        let fullHistoryText = "";
        snapshot.forEach(doc => {
            const conversation = doc.data().messages.slice(1).map(m => `${m.sender}: ${m.text}`).join('\n');
            fullHistoryText += conversation + "\n\n---\n\n";
        });

        const summaryPrompt = `Analyze this agricultural chat history and create a concise "User Interest Profile" summarizing their main interests, crops, problems, and curiosities.\n\nCHAT HISTORY:\n${fullHistoryText}`;
        const summaryPayload = { contents: [{ parts: [{ text: summaryPrompt }] }] };
        const summaryResult = await makeApiCallWithRetry(TEXT_MODEL, summaryPayload);
        const userProfile = summaryResult.candidates?.[0]?.content?.parts?.[0]?.text;
        
        if (!userProfile) throw new Error("Could not extract user profile");

        const recommendationPrompt = `Based on this user profile, provide 3-5 actionable, personalized agricultural recommendations in Markdown format.\n\nUSER PROFILE:\n${userProfile}`;
        const recommendationPayload = { contents: [{ parts: [{ text: recommendationPrompt }] }] };
        const recommendationResult = await makeApiCallWithRetry(TEXT_MODEL, recommendationPayload);
        const recommendations = recommendationResult.candidates?.[0]?.content?.parts?.[0]?.text;
        
        if (!recommendations) throw new Error("Could not extract recommendations");

        res.status(200).json({ recommendations });
    } catch (error) {
        console.error("Error in recommendations:", error);
        res.status(500).json({ error: "Failed to generate recommendations" });
    }
});

app.listen(port, () => {
    console.log(`✅ Combined server running at http://localhost:${port}`);
    console.log(`🌱 Plant Identifier: http://localhost:${port}/`);
    console.log(`💬 Agri-Assistant: http://localhost:${port}/chat`);
});