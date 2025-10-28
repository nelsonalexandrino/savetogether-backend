from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from services.database_service import db
from utils.config import config_by_name
import os

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
    
    # Handle CORS origins (can be string or list)
    cors_origins = app.config.get('CORS_ORIGINS', '')
    if isinstance(cors_origins, str):
        cors_origins = cors_origins.split(',') if cors_origins else []
    
    CORS(app, origins=cors_origins)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.stockvels import stockvels_bp
    from routes.users import users_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(stockvels_bp, url_prefix='/api/stockvels')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    
    @app.route('/')
    def health_check():
        return {'status': 'SaveTogether API is running!', 'version': '1.0.0'}
    
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