from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.stockvel import StockvelMember
from services.database_service import db

users_bp = Blueprint('users', __name__)

@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_current_user_profile():
    try:
        current_user_id = int(get_jwt_identity())  # Convert string back to int
        user = User.get_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get profile', 'details': str(e)}), 500

@users_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    try:
        current_user_id = int(get_jwt_identity())  # Convert string back to int
        
        # Get user stockvel memberships
        memberships = StockvelMember.query.filter_by(user_id=current_user_id).all()
        
        total_stockvels = len(memberships)
        total_contributed = sum(float(m.total_contributed) for m in memberships)
        admin_stockvels = len([m for m in memberships if m.is_admin])
        
        return jsonify({
            'stats': {
                'total_stockvels': total_stockvels,
                'total_contributed': total_contributed,
                'admin_stockvels': admin_stockvels
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get stats', 'details': str(e)}), 500

@users_bp.route('/search', methods=['GET'])
@jwt_required()
def search_users():
    try:
        search_term = request.args.get('q', '').strip()
        
        if not search_term or len(search_term) < 2:
            return jsonify({'users': []}), 200
        
        # Search users by name or email (limit results for privacy)
        users = User.query.filter(
            db.or_(
                User.name.ilike(f'%{search_term}%'),
                User.email.ilike(f'%{search_term}%')
            ),
            User.is_active == True
        ).limit(10).all()
        
        # Return limited user info for privacy
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'name': user.name,
                'email': user.email[:3] + '***@' + user.email.split('@')[1] if '@' in user.email else '***'
            })
        
        return jsonify({'users': users_data}), 200
        
    except Exception as e:
        return jsonify({'error': 'Search failed', 'details': str(e)}), 500