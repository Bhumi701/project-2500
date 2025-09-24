from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.blog import BlogPost
from app.utils.decorators import cache_response
import logging

blog_bp = Blueprint('blog', __name__)
logger = logging.getLogger(__name__)

@blog_bp.route('/', methods=['GET'])
@jwt_required()
@cache_response(timeout=3600)  # Cache for 1 hour
def get_blog_posts():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        category = request.args.get('category')
        language = request.args.get('language', user.preferred_language)
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 50)
        
        query = BlogPost.query.filter_by(language=language, is_published=True)
        
        if category:
            query = query.filter_by(category=category)
        
        posts = query.order_by(BlogPost.created_at.desc())\
                    .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'posts': [post.to_dict() for post in posts.items],
            'total': posts.total,
            'pages': posts.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        logger.error(f"Blog fetch error: {str(e)}")
        return jsonify({'error': 'Failed to fetch blog posts'}), 500

@blog_bp.route('/<int:post_id>', methods=['GET'])
@jwt_required()
def get_blog_post(post_id):
    try:
        post = BlogPost.query.filter_by(id=post_id, is_published=True).first()
        
        if not post:
            return jsonify({'error': 'Blog post not found'}), 404
        
        return jsonify({'post': post.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Blog post fetch error: {str(e)}")
        return jsonify({'error': 'Failed to fetch blog post'}), 500

@blog_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_blog_categories():
    categories = [
        {'id': 'fertilizers', 'name': 'Fertilizers'},
        {'id': 'pesticides', 'name': 'Pesticides'},
        {'id': 'seeds', 'name': 'Seeds & Varieties'},
        {'id': 'irrigation', 'name': 'Irrigation'},
        {'id': 'soil_management', 'name': 'Soil Management'},
        {'id': 'crop_diseases', 'name': 'Crop Diseases'},
        {'id': 'market_trends', 'name': 'Market Trends'},
        {'id': 'government_schemes', 'name': 'Government Schemes'}
    ]
    
    return jsonify({'categories': categories}), 200