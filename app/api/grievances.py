# ========================================
# app/api/grievances.py
# ========================================

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User
from app.models.grievance import Grievance
from app.tasks.email_tasks import send_grievance_notification
from app.utils.validators import validate_grievance_data
import logging

grievances_bp = Blueprint('grievances', __name__)
logger = logging.getLogger(__name__)

@grievances_bp.route('/', methods=['POST'])
@jwt_required()
def submit_grievance():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate grievance data
        validation_result = validate_grievance_data(data)
        if not validation_result['valid']:
            return jsonify({'error': validation_result['message']}), 400
        
        # Create grievance
        grievance = Grievance(
            user_id=user_id,
            subject=data['subject'].strip(),
            description=data['description'].strip(),
            category=data['category'],
            priority=data.get('priority', 'medium')
        )
        
        db.session.add(grievance)
        db.session.commit()
        
        # Send notification to government officials
        send_grievance_notification.delay(grievance.id, user.location)
        
        logger.info(f"New grievance submitted: {grievance.id} by user {user.email}")
        
        return jsonify({
            'message': 'Grievance submitted successfully',
            'grievance': grievance.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Grievance submission error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Grievance submission failed'}), 500

@grievances_bp.route('/', methods=['GET'])
@jwt_required()
def get_user_grievances():
    try:
        user_id = get_jwt_identity()
        
        status = request.args.get('status')
        category = request.args.get('category')
        
        query = Grievance.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        if category:
            query = query.filter_by(category=category)
        
        grievances = query.order_by(Grievance.created_at.desc()).all()  # grievance records ko latest date ke descending order mein fetch karna

        
        return jsonify({
            'grievances': [grievance.to_dict() for grievance in grievances]
        }), 200
        
    except Exception as e:
        logger.error(f"Grievances fetch error: {str(e)}")
        return jsonify({'error': 'Failed to fetch grievances'}), 500

@grievances_bp.route('/<int:grievance_id>', methods=['GET'])
@jwt_required()
def get_grievance_details(grievance_id):
    try:
        user_id = get_jwt_identity()
        
        grievance = Grievance.query.filter_by(
            id=grievance_id, 
            user_id=user_id
        ).first()
        
        if not grievance:
            return jsonify({'error': 'Grievance not found'}), 404
        
        return jsonify({'grievance': grievance.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Grievance details error: {str(e)}")
        return jsonify({'error': 'Failed to fetch grievance details'}), 500

@grievances_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_grievance_categories():
    categories = [
        {'id': 'crop_insurance', 'name': 'Crop Insurance'},
        {'id': 'subsidies', 'name': 'Subsidies'},
        {'id': 'loan_issues', 'name': 'Loan Issues'},
        {'id': 'market_access', 'name': 'Market Access'},
        {'id': 'water_supply', 'name': 'Water Supply'},
        {'id': 'pest_control', 'name': 'Pest Control'},
        {'id': 'other', 'name': 'Other'}
    ]
    
    return jsonify({'categories': categories}), 200