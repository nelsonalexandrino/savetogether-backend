from flask import Blueprint, jsonify, render_template
from models.user import User
from models.stockvel import Stockvel, StockvelMember
from services.database_service import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/panel')
def admin_panel():
    """Serve the admin HTML page"""
    return render_template('admin.html')

@admin_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        total_stockvels = Stockvel.query.count()
        
        return jsonify({
            'total_users': total_users,
            'active_users': active_users,
            'total_stockvels': total_stockvels
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error getting stats: {str(e)}'}), 500

@admin_bp.route('/users', methods=['GET'])
def get_all_users():
    """Get all users"""
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error getting users: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a specific user"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        email = user.email
        
        # Delete user (cascade will handle related records if configured)
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'message': f'User {email} deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error deleting user: {str(e)}'}), 500

@admin_bp.route('/users/delete-all', methods=['POST'])
def delete_all_users():
    """Delete all users - USE WITH CAUTION"""
    try:
        # First delete all stockvel members
        StockvelMember.query.delete()
        
        # Then delete all stockvels
        Stockvel.query.delete()
        
        # Finally delete all users
        num_deleted = User.query.delete()
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully deleted {num_deleted} users and all related data'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error deleting users: {str(e)}'}), 500

@admin_bp.route('/stockvels', methods=['GET'])
def get_all_stockvels():
    """Get all stockvels/groups"""
    try:
        stockvels = Stockvel.query.order_by(Stockvel.created_at.desc()).all()
        
        stockvels_data = []
        for stockvel in stockvels:
            stockvel_dict = stockvel.to_dict()
            # Add admin user info
            admin = User.query.get(stockvel.admin_user_id)
            stockvel_dict['admin'] = admin.to_dict() if admin else None
            # Add member count
            stockvel_dict['member_count'] = len(stockvel.members)
            stockvels_data.append(stockvel_dict)
        
        return jsonify({
            'stockvels': stockvels_data
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error getting stockvels: {str(e)}'}), 500

@admin_bp.route('/stockvels/<int:stockvel_id>', methods=['DELETE'])
def delete_stockvel(stockvel_id):
    """Delete a specific stockvel"""
    try:
        stockvel = Stockvel.query.get(stockvel_id)
        
        if not stockvel:
            return jsonify({'message': 'Stockvel not found'}), 404
        
        name = stockvel.name
        
        # Delete related records first
        StockvelMember.query.filter_by(stockvel_id=stockvel_id).delete()
        
        # Delete stockvel
        db.session.delete(stockvel)
        db.session.commit()
        
        return jsonify({
            'message': f'Stockvel "{name}" deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error deleting stockvel: {str(e)}'}), 500

@admin_bp.route('/stockvels/delete-all', methods=['POST'])
def delete_all_stockvels():
    """Delete all stockvels - USE WITH CAUTION"""
    try:
        # First delete all members
        StockvelMember.query.delete()
        
        # Then delete all stockvels
        num_deleted = Stockvel.query.delete()
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully deleted {num_deleted} stockvels and all related data'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error deleting stockvels: {str(e)}'}), 500

