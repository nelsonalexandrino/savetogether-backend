from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Initialize database with app"""
    db.init_app(app)
    
def create_tables():
    """Create all database tables"""
    db.create_all()
    
def drop_tables():
    """Drop all database tables"""
    db.drop_all()