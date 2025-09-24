import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class PolicyService:
    def __init__(self):
        self.base_url = "https://api.data.gov.in"  # Government of India Open Data API
        self.kerala_agri_dept_url = "https://keralaagriculture.gov.in"
        
        # Cache for policies (in production, use Redis)
        self._policy_cache = {}
        self._seed_cost_cache = {}
        self._cache_timeout = 3600  # 1 hour
    
    def get_policies(self, language='en', category=None, state='kerala'):
        """Get government agricultural policies"""
        try:
            cache_key = f"policies_{language}_{category}_{state}"
            
            # Check cache first
            if self._is_cache_valid(cache_key):
                return self._policy_cache[cache_key]['data']
            
            # Fetch policies from multiple sources
            policies = []
            
            # Kerala state policies
            kerala_policies = self._get_kerala_policies(language, category)
            policies.extend(kerala_policies)
            
            # Central government policies
            central_policies = self._get_central_policies(language, category)
            policies.extend(central_policies)
            
            # Cache the results
            self._policy_cache[cache_key] = {
                'data': policies,
                'timestamp': datetime.utcnow()
            }
            
            return policies
            
        except Exception as e:
            logger.error(f"Policy fetch error: {str(e)}")
            return self._get_fallback_policies(language, category)
    
    def get_seed_costs(self, location, crop_type=None):
        """Get current seed costs and market prices"""
        try:
            cache_key = f"seed_costs_{location}_{crop_type}"
            
            # Check cache
            if self._is_cache_valid(cache_key, timeout=1800):  # 30 minutes
                return self._seed_cost_cache[cache_key]['data']
            
            # Fetch seed costs
            seed_costs = []
            
            # Get from multiple sources
            agmarknet_data = self._get_agmarknet_prices(location, crop_type)
            seed_costs.extend(agmarknet_data)
            
            # Add local market data
            local_data = self._get_local_seed_costs(location, crop_type)
            seed_costs.extend(local_data)
            
            # Cache results
            self._seed_cost_cache[cache_key] = {
                'data': seed_costs,
                'timestamp': datetime.utcnow()
            }
            
            return seed_costs
            
        except Exception as e:
            logger.error(f"Seed cost fetch error: {str(e)}")
            return self._get_fallback_seed_costs(location, crop_type)
    
    def get_subsidies(self, farmer_category='general', state='kerala'):
        """Get available subsidies for farmers"""
        try:
            subsidies = []
            
            # Kerala state subsidies
            kerala_subsidies = [
                {
                    'name': 'Kerala Agricultural Development Scheme',
                    'description': 'Financial assistance for modern farming equipment and techniques',
                    'amount': '50% subsidy up to ₹50,000',
                    'eligibility': 'Small and marginal farmers',
                    'category': 'equipment',
                    'application_process': 'Apply through District Collector office',
                    'documents_required': ['Land documents', 'Aadhaar card', 'Bank account details'],
                    'deadline': '31st March 2024',
                    'contact': '0471-2301234'
                },
                {
                    'name': 'Organic Farming Promotion Scheme',
                    'description': 'Support for transition to organic farming practices',
                    'amount': '₹20,000 per hectare for 3 years',
                    'eligibility': 'All categories of farmers',
                    'category': 'organic_farming',
                    'application_process': 'Online application through Kerala Agriculture Portal',
                    'documents_required': ['Soil test report', 'Land records', 'Training certificate'],
                    'deadline': 'Ongoing',
                    'contact': 'organicfarming@kerala.gov.in'
                },
                {
                    'name': 'Micro Irrigation Subsidy',
                    'description': 'Subsidy for drip and sprinkler irrigation systems',
                    'amount': '90% subsidy for SC/ST, 75% for others',
                    'eligibility': 'Farmers with minimum 0.1 hectare land',
                    'category': 'irrigation',
                    'application_process': 'Apply through Agriculture Department',
                    'documents_required': ['Survey settlement', 'Water source certificate'],
                    'deadline': 'Year-round',
                    'contact': '0471-2305678'
                }
            ]
            
            subsidies.extend(kerala_subsidies)
            
            # Central government subsidies
            central_subsidies = [
                {
                    'name': 'PM-KISAN Scheme',
                    'description': 'Income support of ₹6000 per year to farmer families',
                    'amount': '₹2000 per installment (3 times a year)',
                    'eligibility': 'All landholding farmer families',
                    'category': 'income_support',
                    'application_process': 'Online registration at pmkisan.gov.in',
                    'documents_required': ['Aadhaar card', 'Bank account', 'Land ownership proof'],
                    'deadline': 'Ongoing',
                    'contact': '155261'
                },
                {
                    'name': 'Soil Health Card Scheme',
                    'description': 'Free soil testing and health cards for farmers',
                    'amount': 'Free service',
                    'eligibility': 'All farmers',
                    'category': 'soil_testing',
                    'application_process': 'Contact local Agriculture Extension Officer',
                    'documents_required': ['Land documents'],
                    'deadline': 'Ongoing',
                    'contact': 'Local Agriculture Office'
                }
            ]
            
            subsidies.extend(central_subsidies)
            
            # Filter by farmer category if specified
            if farmer_category != 'general':
                subsidies = [s for s in subsidies if farmer_category in s.get('eligibility', '').lower()]
            
            return subsidies
            
        except Exception as e:
            logger.error(f"Subsidies fetch error: {str(e)}")
            return []
    
    def get_market_prices(self, commodity, market_location='kerala'):
        """Get current market prices for agricultural commodities"""
        try:
            # This would integrate with AGMARKNET API
            # For now, returning mock data with realistic prices
            
            prices = [
                {
                    'commodity': 'Rice',
                    'variety': 'Basmati',
                    'market': 'Thrissur',
                    'price_per_quintal': 4500,
                    'price_trend': 'stable',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'quality': 'FAQ (Fair Average Quality)'
                },
                {
                    'commodity': 'Rice',
                    'variety': 'Common',
                    'market': 'Kochi',
                    'price_per_quintal': 2800,
                    'price_trend': 'increasing',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'quality': 'Medium'
                },
                {
                    'commodity': 'Coconut',
                    'variety': 'Mature',
                    'market': 'Kozhikode',
                    'price_per_piece': 25,
                    'price_trend': 'stable',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'quality': 'Good'
                },
                {
                    'commodity': 'Black Pepper',
                    'variety': 'Dried',
                    'market': 'Idukki',
                    'price_per_kg': 850,
                    'price_trend': 'increasing',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'quality': 'Superior'
                },
                {
                    'commodity': 'Cardamom',
                    'variety': 'Small',
                    'market': 'Kumily',
                    'price_per_kg': 1200,
                    'price_trend': 'decreasing',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'quality': 'Premium'
                }
            ]
            
            # Filter by commodity if specified
            if commodity:
                prices = [p for p in prices if commodity.lower() in p['commodity'].lower()]
            
            return prices
            
        except Exception as e:
            logger.error(f"Market prices fetch error: {str(e)}")
            return []
    
    def _get_kerala_policies(self, language='en', category=None):
        """Fetch Kerala state agricultural policies"""
        policies = [
            {
                'id': 'KL001',
                'title': 'Kerala Agricultural Development Scheme 2024' if language == 'en' else 'കേരള കാർഷിക വികസന പദ്ധതി 2024',
                'description': 'Comprehensive scheme for agricultural modernization and farmer welfare' if language == 'en' else 'കാർഷിക ആധുനികവൽക്കരണത്തിനും കർഷക ക്ഷേമത്തിനുമുള്ള സമഗ്ര പദ്ധതി',
                'category': 'development',
                'state': 'kerala',
                'department': 'Department of Agriculture, Kerala',
                'launched_date': '2024-01-01',
                'valid_until': '2024-12-31',
                'budget': '₹500 crores',
                'beneficiaries': 'All categories of farmers',
                'key_features': [
                    'Subsidized farm equipment',
                    'Free soil testing',
                    'Training programs',
                    'Market linkage support'
                ],
                'application_process': 'Online through Kerala Agriculture Portal',
                'contact': {
                    'phone': '0471-2301234',
                    'email': 'agri@kerala.gov.in',
                    'website': 'https://keralaagriculture.gov.in'
                },
                'language': language
            },
            {
                'id': 'KL002',
                'title': 'Organic Kerala Mission' if language == 'en' else 'ഓർഗാനിക് കേരള മിഷൻ',
                'description': 'State-wide initiative to promote organic farming practices' if language == 'en' else 'ജൈവകൃഷി രീതികൾ പ്രോത്സാഹിപ്പിക്കുന്നതിനുള്ള സംസ്ഥാനവ്യാപക സംരംഭം',
                'category': 'organic_farming',
                'state': 'kerala',
                'department': 'Department of Agriculture, Kerala',
                'launched_date': '2023-06-01',
                'valid_until': '2026-05-31',
                'budget': '₹200 crores',
                'beneficiaries': 'Farmers willing to adopt organic practices',
                'key_features': [
                    'Organic certification support',
                    'Bio-fertilizer subsidies',
                    'Premium price guarantee',
                    'Export promotion'
                ],
                'application_process': 'District Agriculture Development Officer',
                'contact': {
                    'phone': '0471-2305678',
                    'email': 'organic@kerala.gov.in',
                    'website': 'https://organickerala.gov.in'
                },
                'language': language
            }
        ]
        
        # Filter by category if specified
        if category:
            policies = [p for p in policies if p['category'] == category]
        
        return policies
    
    def _get_central_policies(self, language='en', category=None):
        """Fetch central government agricultural policies"""
        policies = [
            {
                'id': 'IN001',
                'title': 'PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)',
                'description': 'Income support scheme providing ₹6000 per year to farmer families',
                'category': 'income_support',
                'state': 'all_india',
                'department': 'Ministry of Agriculture & Farmers Welfare',
                'launched_date': '2019-02-01',
                'valid_until': 'ongoing',
                'budget': '₹75,000 crores (2024-25)',
                'beneficiaries': 'Small and marginal farmer families',
                'key_features': [
                    'Direct cash transfer',
                    'Three installments per year',
                    'Aadhaar-linked payments',
                    'No paperwork for existing beneficiaries'
                ],
                'application_process': 'Online at pmkisan.gov.in or Common Service Centers',
                'contact': {
                    'phone': '155261',
                    'email': 'pmkisan-ict@gov.in',
                    'website': 'https://pmkisan.gov.in'
                },
                'language': language
            },
            {
                'id': 'IN002',
                'title': 'Pradhan Mantri Fasal Bima Yojana (PMFBY)',
                'description': 'Crop insurance scheme providing coverage against crop loss',
                'category': 'insurance',
                'state': 'all_india',
                'department': 'Ministry of Agriculture & Farmers Welfare',
                'launched_date': '2016-01-01',
                'valid_until': 'ongoing',
                'budget': '₹16,000 crores (2024-25)',
                'beneficiaries': 'All farmers including sharecroppers and tenant farmers',
                'key_features': [
                    'Low premium rates',
                    'Coverage for all stages of crop cycle',
                    'Use of technology for quick settlement',
                    'Voluntary for all farmers'
                ],
                'application_process': 'Banks, Insurance Companies, or online',
                'contact': {
                    'phone': '011-20096742',
                    'email': 'pmfby@gov.in',
                    'website': 'https://pmfby.gov.in'
                },
                'language': language
            }
        ]
        
        if category:
            policies = [p for p in policies if p['category'] == category]
        
        return policies
    
    def _get_agmarknet_prices(self, location, crop_type=None):
        """Fetch prices from AGMARKNET (mock implementation)"""
        # In production, this would call the actual AGMARKNET API
        seed_costs = [
            {
                'crop': 'Rice',
                'variety': 'Ponni',
                'seed_type': 'Hybrid',
                'price_per_kg': 150,
                'price_per_quintal': 15000,
                'availability': 'High',
                'quality': 'Certified',
                'location': location,
                'supplier': 'Kerala State Seeds Corporation',
                'contact': '0471-2345678',
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            },
            {
                'crop': 'Rice',
                'variety': 'Basmati',
                'seed_type': 'Pure',
                'price_per_kg': 200,
                'price_per_quintal': 20000,
                'availability': 'Medium',
                'quality': 'Certified',
                'location': location,
                'supplier': 'Private Dealer',
                'contact': '9876543210',
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            }
        ]
        
        if crop_type:
            seed_costs = [s for s in seed_costs if crop_type.lower() in s['crop'].lower()]
        
        return seed_costs
    
    def _get_local_seed_costs(self, location, crop_type=None):
        """Get local seed costs from regional suppliers"""
        local_costs = [
            {
                'crop': 'Coconut',
                'variety': 'Dwarf',
                'seed_type': 'Seedlings',
                'price_per_piece': 45,
                'availability': 'High',
                'quality': 'Good',
                'location': location,
                'supplier': 'Local Nursery',
                'contact': '9876543211',
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            },
            {
                'crop': 'Banana',
                'variety': 'Robusta',
                'seed_type': 'Tissue Culture',
                'price_per_piece': 12,
                'availability': 'High',
                'quality': 'Excellent',
                'location': location,
                'supplier': 'Horticorp Kerala',
                'contact': '0471-2567890',
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            }
        ]
        
        if crop_type:
            local_costs = [s for s in local_costs if crop_type.lower() in s['crop'].lower()]
        
        return local_costs
    
    def _get_fallback_policies(self, language='en', category=None):
        """Fallback policies when API is unavailable"""
        fallback = [
            {
                'id': 'FALLBACK001',
                'title': 'Basic Agricultural Support Scheme' if language == 'en' else 'അടിസ്ഥാന കാർഷിക സഹായ പദ്ധതി',
                'description': 'General agricultural support available to all farmers' if language == 'en' else 'എല്ലാ കർഷകർക്കും ലഭ്യമായ പൊതു കാർഷിക സഹായം',
                'category': 'general',
                'state': 'kerala',
                'department': 'Agriculture Department',
                'key_features': ['Basic subsidies', 'Technical support', 'Training programs'],
                'contact': {
                    'phone': '0471-2301234',
                    'email': 'info@agriculture.kerala.gov.in'
                },
                'language': language
            }
        ]
        
        return fallback
    
    def _get_fallback_seed_costs(self, location, crop_type=None):
        """Fallback seed costs when API is unavailable"""
        fallback = [
            {
                'crop': 'Rice',
                'variety': 'Common',
                'price_per_kg': 120,
                'availability': 'Available',
                'location': location,
                'supplier': 'Local Supplier',
                'last_updated': datetime.now().strftime('%Y-%m-%d'),
                'note': 'Approximate prices - contact local supplier for current rates'
            }
        ]
        
        if crop_type:
            fallback = [s for s in fallback if crop_type.lower() in s['crop'].lower()]
        
        return fallback
    
    def _is_cache_valid(self, cache_key, timeout=None):
        """Check if cached data is still valid"""
        if cache_key not in self._policy_cache and cache_key not in self._seed_cost_cache:
            return False
        
        cache_timeout = timeout or self._cache_timeout
        cache_data = self._policy_cache.get(cache_key) or self._seed_cost_cache.get(cache_key)
        
        if not cache_data:
            return False
        
        time_diff = datetime.utcnow() - cache_data['timestamp']
        return time_diff.seconds < cache_timeout