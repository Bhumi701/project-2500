from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.services.policy_service import PolicyService
from app.utils.decorators import cache_response
import logging

policies_bp = Blueprint('policies', __name__)
logger = logging.getLogger(__name__)

@policies_bp.route('/', methods=['GET'])
@jwt_required()
@cache_response(timeout=3600)  # Cache for 1 hour
def get_policies():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        language = request.args.get('language', user.preferred_language)
        category = request.args.get('category')
        
        policy_service = PolicyService()
        policies = policy_service.get_policies(
            language=language,
            category=category,
            state='kerala'
        )
        
        return jsonify({'policies': policies}), 200
        
    except Exception as e:
        logger.error(f"Policies fetch error: {str(e)}")
        return jsonify({'error': 'Failed to fetch policies'}), 500

@policies_bp.route('/seed-costs', methods=['GET'])
@jwt_required()
@cache_response(timeout=1800)  # Cache for 30 minutes
def get_seed_costs():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        crop_type = request.args.get('crop_type')
        
        policy_service = PolicyService()
        seed_costs = policy_service.get_seed_costs(
            location=user.location,
            crop_type=crop_type
        )
        
        return jsonify({'seed_costs': seed_costs}), 200
        
    except Exception as e:
        logger.error(f"Seed costs fetch error: {str(e)}")
        return jsonify({'error': 'Failed to fetch seed costs'}), 500