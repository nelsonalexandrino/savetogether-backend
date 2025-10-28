from flask import Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from services.database_service import db
from utils.config import config_by_name
import os
import logging

# Initialize JWT extension
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    config_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config_by_name[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    # JWT error handlers for better error messages
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'message': 'Token has expired', 'error': 'token_expired'}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(f"Invalid token error: {error}")
        return {'message': f'Invalid token: {error}', 'error': 'invalid_token'}, 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        print(f"Unauthorized error: {error}")
        return {'message': f'Authorization token is missing: {error}', 'error': 'missing_token'}, 401
    
    # Handle CORS origins (can be string or list)
    cors_origins = app.config.get('CORS_ORIGINS', '')
    if isinstance(cors_origins, str):
        cors_origins = cors_origins.split(',') if cors_origins else []
    
    CORS(app, origins=cors_origins)
    
    # Add request logging middleware
    @app.before_request
    def log_request_info():
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Request: {request.method} {request.path}")
        logger.info(f"Headers: {dict(request.headers)}")
        if request.headers.get('Authorization'):
            auth_header = request.headers.get('Authorization')
            logger.info(f"Auth Header: {auth_header[:50]}...")
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.stockvels import stockvels_bp
    from routes.users import users_bp
    from routes.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(stockvels_bp, url_prefix='/api/stockvels')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    @app.route('/')
    def health_check():
        return {'status': 'SaveTogether API is running!', 'version': '1.0.0'}
    
    @app.route('/test-auth')
    def test_auth():
        """Test endpoint to check JWT configuration"""
        from flask_jwt_extended import create_access_token
        import os
        
        # Create a test token
        test_token = create_access_token(identity=999)
        jwt_secret = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
        
        return {
            'message': 'JWT is configured',
            'jwt_secret_preview': jwt_secret[:10] + '...',
            'test_token': test_token[:50] + '...',
            'full_test_token': test_token
        }
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Import models to ensure they're registered
        from models.user import User
        from models.stockvel import Stockvel, StockvelMember, Contribution
        
    app.run(
        host=app.config.get('HOST', '0.0.0.0'),
        port=app.config.get('PORT', 5000),
        debug=app.config.get('DEBUG', False)
    )