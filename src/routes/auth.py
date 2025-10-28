from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from models.user import User
from services.database_service import db
import re
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/debug', methods=['GET'])
def debug_jwt():
    """Debug endpoint to check JWT configuration"""
    import os
    from flask import current_app
    
    jwt_secret = os.getenv('JWT_SECRET_KEY', 'NOT SET')
    app_jwt_secret = current_app.config.get('JWT_SECRET_KEY', 'NOT SET')
    
    return jsonify({
        'env_jwt_secret': jwt_secret[:15] + '...' if jwt_secret != 'NOT SET' else 'NOT SET',
        'app_jwt_secret': app_jwt_secret[:15] + '...' if app_jwt_secret != 'NOT SET' else 'NOT SET',
        'flask_env': os.getenv('FLASK_ENV', 'NOT SET'),
        'debug': current_app.config.get('DEBUG', 'NOT SET')
    }), 200

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user with email and password"""
    try:
        data = request.get_json()
        
        # Validate required fields
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400
        
        if not validate_email(email):
            return jsonify({'message': 'Invalid email format'}), 400
        
        if len(password) < 6:
            return jsonify({'message': 'Password must be at least 6 characters long'}), 400
        
        # Check if user already exists
        existing_user = User.get_by_email(email)
        if existing_user:
            return jsonify({'message': 'User with this email already exists'}), 409
        
        # Create new user
        display_name = data.get('display_name', email.split('@')[0])  # Default to email prefix
        phone = data.get('phone', '').strip() if data.get('phone') else None
        
        user = User(
            email=email,
            display_name=display_name,
            phone=phone
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Generate access token (identity as string)
        access_token = create_access_token(identity=str(user.id))
        logger.info(f"Generated token for user {user.id}: {access_token[:20]}...")
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user with email and password"""
    try:
        data = request.get_json()
        
        # Validate required fields
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400
        
        # Find user by email
        user = User.get_by_email(email)
        
        if not user:
            return jsonify({'message': 'Invalid email or password'}), 401
        
        # Check password
        if not user.check_password(password):
            return jsonify({'message': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'message': 'Account is deactivated'}), 401
        
        # Update last login
        from datetime import datetime
        import os
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate access token
        access_token = create_access_token(identity=str(user.id))
        jwt_secret = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
        logger.info(f"Login successful for user {user.id} ({user.email})")
        logger.info(f"JWT Secret being used: {jwt_secret[:10]}...")
        logger.info(f"Generated token: {access_token[:50]}...")
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict(),
            'debug_jwt_secret_preview': jwt_secret[:10] + '...'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user's profile"""
    try:
        user_id = int(get_jwt_identity())  # Convert string back to int
        logger.info(f"Profile request from user_id: {user_id}")
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user's profile"""
    try:
        current_user_id = int(get_jwt_identity())  # Convert string back to int
        user = User.get_by_id(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'display_name' in data:
            user.display_name = data['display_name'].strip()
        if 'phone' in data:
            user.phone = data['phone'].strip() if data['phone'] else None
        if 'profile_image' in data:
            user.profile_image = data['profile_image']
            
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        current_user_id = int(get_jwt_identity())  # Convert string back to int
        user = User.get_by_id(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        
        if not old_password or not new_password:
            return jsonify({'message': 'Old password and new password are required'}), 400
        
        if not user.check_password(old_password):
            return jsonify({'message': 'Invalid old password'}), 401
        
        if len(new_password) < 6:
            return jsonify({'message': 'New password must be at least 6 characters long'}), 400
        
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500