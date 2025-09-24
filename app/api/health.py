from flask import Blueprint, jsonify
from datetime import datetime

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'success',
        'message': 'KrishiSphere backend is healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 200