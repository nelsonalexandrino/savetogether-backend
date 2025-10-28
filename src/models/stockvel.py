from services.database_service import db
from datetime import datetime
from sqlalchemy import Numeric
import random
import string

class Stockvel(db.Model):
    __tablename__ = 'stockvels'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    contribution_amount = db.Column(Numeric(10, 2), nullable=False)  # contributionAmount from Flutter
    frequency = db.Column(db.String(20), nullable=False)  # Weekly, Bi-Weekly, Monthly
    max_members = db.Column(db.Integer, nullable=False)  # maxMembers from Flutter
    start_date = db.Column(db.DateTime, nullable=False)  # startDate from Flutter
    end_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='Upcoming')  # status from Flutter
    invite_code = db.Column(db.String(10), unique=True, nullable=False)  # inviteCode from Flutter
    admin_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # adminUser from Flutter
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # createdAt from Flutter
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    members = db.relationship('StockvelMember', backref='stockvel', lazy=True, cascade='all, delete-orphan')
    contributions = db.relationship('Contribution', backref='stockvel', lazy=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.invite_code:
            self.invite_code = self.generate_invite_code()
    
    @staticmethod
    def generate_invite_code():
        """Generate a unique 6-character invite code like Flutter's _generateInviteCode"""
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
        while True:
            code = ''.join(random.choice(chars) for _ in range(6))
            # Check if code already exists
            if not Stockvel.query.filter_by(invite_code=code).first():
                return code

    def __repr__(self):
        return f"<Stockvel(id={self.id}, name='{self.name}', invite_code='{self.invite_code}')>"

    def to_dict(self):
        """Convert stockvel object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'contribution_amount': float(self.contribution_amount),
            'frequency': self.frequency,
            'max_members': self.max_members,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'invite_code': self.invite_code,
            'admin_user_id': self.admin_user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'member_count': len(self.members),
            'target_amount': float(self.contribution_amount) * self.max_members,
            'current_total': sum(float(c.amount) for c in self.contributions)
        }

class StockvelMember(db.Model):
    __tablename__ = 'stockvel_members'

    id = db.Column(db.Integer, primary_key=True)
    stockvel_id = db.Column(db.Integer, db.ForeignKey('stockvels.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)  # Track if this member is admin
    is_active = db.Column(db.Boolean, default=True)

    # Unique constraint to prevent duplicate memberships
    __table_args__ = (db.UniqueConstraint('stockvel_id', 'user_id', name='unique_stockvel_member'),)

    def to_dict(self):
        return {
            'id': self.id,
            'stockvel_id': self.stockvel_id,
            'user_id': self.user_id,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'is_admin': self.is_admin,
            'is_active': self.is_active
        }

class Contribution(db.Model):
    __tablename__ = 'contributions'

    id = db.Column(db.Integer, primary_key=True)
    stockvel_id = db.Column(db.Integer, db.ForeignKey('stockvels.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(Numeric(10, 2), nullable=False)
    contribution_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(255), nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)  # bank_transfer, cash, etc.
    status = db.Column(db.String(20), default='confirmed')  # pending, confirmed, failed

    def to_dict(self):
        return {
            'id': self.id,
            'stockvel_id': self.stockvel_id,
            'user_id': self.user_id,
            'amount': float(self.amount),
            'contribution_date': self.contribution_date.isoformat() if self.contribution_date else None,
            'description': self.description,
            'payment_method': self.payment_method,
            'status': self.status
        }