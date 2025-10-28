from services.database_service import db
from datetime import datetime

class Stockvel(db.Model):
    __tablename__ = 'stockvels'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    target_amount = db.Column(db.Decimal(10, 2), nullable=False)
    current_amount = db.Column(db.Decimal(10, 2), default=0.00)
    monthly_contribution = db.Column(db.Decimal(10, 2), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    max_members = db.Column(db.Integer, default=10)
    
    # Relationships
    members = db.relationship('StockvelMember', backref='stockvel', lazy=True, cascade='all, delete-orphan')
    contributions = db.relationship('Contribution', backref='stockvel', lazy=True)

    def __repr__(self):
        return f"<Stockvel(id={self.id}, name='{self.name}', target_amount={self.target_amount})>"

    def to_dict(self):
        """Convert stockvel object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'target_amount': float(self.target_amount),
            'current_amount': float(self.current_amount),
            'monthly_contribution': float(self.monthly_contribution),
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'max_members': self.max_members,
            'member_count': len(self.members)
        }

class StockvelMember(db.Model):
    __tablename__ = 'stockvel_members'

    id = db.Column(db.Integer, primary_key=True)
    stockvel_id = db.Column(db.Integer, db.ForeignKey('stockvels.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    total_contributed = db.Column(db.Decimal(10, 2), default=0.00)

    def to_dict(self):
        return {
            'id': self.id,
            'stockvel_id': self.stockvel_id,
            'user_id': self.user_id,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'is_admin': self.is_admin,
            'total_contributed': float(self.total_contributed)
        }

class Contribution(db.Model):
    __tablename__ = 'contributions'

    id = db.Column(db.Integer, primary_key=True)
    stockvel_id = db.Column(db.Integer, db.ForeignKey('stockvels.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Decimal(10, 2), nullable=False)
    contribution_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'stockvel_id': self.stockvel_id,
            'user_id': self.user_id,
            'amount': float(self.amount),
            'contribution_date': self.contribution_date.isoformat() if self.contribution_date else None,
            'description': self.description
        }