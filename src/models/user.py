from services.database_service import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)  # email from Flutter
    display_name = db.Column(db.String(100), nullable=True)  # displayName from Flutter
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)  # For future profile images
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    stockvel_memberships = db.relationship('StockvelMember', backref='user', lazy=True)
    contributions = db.relationship('Contribution', backref='user', lazy=True)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', display_name='{self.display_name}')>"

    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_joined_group_ids(self):
        """Get list of stockvel IDs this user is a member of (matches Flutter's joinedGroupIds)"""
        return [membership.stockvel_id for membership in self.stockvel_memberships if membership.is_active]

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'display_name': self.display_name,
            'phone': self.phone,
            'profile_image': self.profile_image,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'joined_group_ids': self.get_joined_group_ids()  # matches Flutter's joinedGroupIds
        }
    
    def to_public_dict(self):
        """Public version for showing in group member lists"""
        return {
            'id': self.id,
            'email': self.email,
            'display_name': self.display_name,
            'profile_image': self.profile_image
        }

    @classmethod
    def create_user(cls, email, display_name, password, phone=None):
        """Create a new user"""
        user = cls(email=email, display_name=display_name, phone=phone)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def get_by_email(cls, email):
        """Get user by email"""
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_by_id(cls, user_id):
        """Get user by ID"""
        return cls.query.get(user_id)