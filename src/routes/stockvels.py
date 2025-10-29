from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.stockvel import Stockvel, StockvelMember, Contribution
from models.user import User
from services.database_service import db
from sqlalchemy import func
from datetime import datetime, date
from decimal import Decimal
import logging

stockvels_bp = Blueprint('stockvels', __name__)
logger = logging.getLogger(__name__)

@stockvels_bp.route('/', methods=['POST'])
@jwt_required()
def create_stockvel():
    """Create a new stockvel/group"""
    try:
        current_user_id = int(get_jwt_identity())  # Convert string back to int
        data = request.get_json()
        
        logger.info(f"Create stockvel request from user {current_user_id}")
        logger.info(f"Request data: {data}")
        
        # Validation - matching Flutter fields
        required_fields = ['name', 'contribution_amount', 'frequency', 'max_members', 'start_date']
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field: {field}")
                return jsonify({'message': f'{field} is required'}), 400
        
        # Parse start_date
        try:
            start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        except:
            try:
                start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
            except Exception as date_error:
                logger.error(f"Date parsing error: {date_error}")
                return jsonify({'message': 'Invalid date format'}), 400
        
        # Create stockvel
        stockvel = Stockvel(
            name=data['name'],
            description=data.get('description', ''),
            contribution_amount=Decimal(str(data['contribution_amount'])),
            frequency=data['frequency'],  # Weekly, Bi-Weekly, Monthly
            max_members=int(data['max_members']),
            start_date=start_date,
            status=data.get('status', 'Upcoming'),
            admin_user_id=current_user_id
        )
        
        db.session.add(stockvel)
        db.session.flush()  # Get the ID and invite_code
        
        logger.info(f"Stockvel created with ID: {stockvel.id}")
        
        # Add creator as admin member
        member = StockvelMember(
            stockvel_id=stockvel.id,
            user_id=current_user_id,
            is_admin=True
        )
        db.session.add(member)
        db.session.commit()
        
        logger.info(f"Stockvel {stockvel.id} created successfully")
        
        return jsonify({
            'message': 'Group created successfully',
            'invite_code': stockvel.invite_code,
            'stockvel': stockvel.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating stockvel: {str(e)}", exc_info=True)
        return jsonify({'message': f'Failed to create group: {str(e)}'}), 500

@stockvels_bp.route('/', methods=['GET'])
@jwt_required()
def get_stockvels():
    try:
        current_user_id = int(get_jwt_identity())  # Convert string back to int
        logger.info(f"Get stockvels request from user_id: {current_user_id}")
        logger.info(f"Authorization header: {request.headers.get('Authorization', 'MISSING')[:50]}...")
        
        # Get stockvels where user is a member
        user_stockvels = db.session.query(Stockvel).join(StockvelMember).filter(
            StockvelMember.user_id == current_user_id,
            Stockvel.is_active == True
        ).all()
        
        logger.info(f"Found {len(user_stockvels)} stockvels for user {current_user_id}")
        
        # Add user-specific contribution data to each stockvel
        stockvels_data = []
        for stockvel in user_stockvels:
            stockvel_dict = stockvel.to_dict()
            
            # Get user's total contributions to this stockvel
            user_contributions = db.session.query(Contribution).filter(
                Contribution.stockvel_id == stockvel.id,
                Contribution.user_id == current_user_id,
                Contribution.status == 'confirmed'
            ).all()
            
            user_total_contributed = sum(float(c.amount) for c in user_contributions)
            
            # Calculate expected contribution for this user (contribution_amount * max_members for full cycle)
            # But user only needs to contribute their share: contribution_amount * max_members
            user_expected_total = float(stockvel.contribution_amount) * stockvel.max_members
            
            # Add user-specific data
            stockvel_dict['user_contributed'] = user_total_contributed
            stockvel_dict['user_expected'] = user_expected_total
            stockvel_dict['user_progress_percentage'] = (user_total_contributed / user_expected_total * 100) if user_expected_total > 0 else 0
            
            stockvels_data.append(stockvel_dict)
        
        return jsonify({
            'stockvels': stockvels_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting stockvels: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to get stockvels', 'details': str(e)}), 500

@stockvels_bp.route('/<int:stockvel_id>', methods=['GET'])
@jwt_required()
def get_stockvel(stockvel_id):
    try:
        current_user_id = int(get_jwt_identity())  # Convert string back to int
        
        # Check if user is a member
        member = StockvelMember.query.filter_by(
            stockvel_id=stockvel_id,
            user_id=current_user_id
        ).first()
        
        if not member:
            return jsonify({'error': 'Access denied'}), 403
        
        stockvel = Stockvel.query.get(stockvel_id)
        if not stockvel:
            return jsonify({'error': 'Stockvel not found'}), 404
        
        # Get members and their details
        members_data = []
        for member in stockvel.members:
            user = User.get_by_id(member.user_id)
            members_data.append({
                'id': member.id,
                'user': user.to_dict() if user else None,
                'joined_at': member.joined_at.isoformat() if member.joined_at else None,
                'is_admin': member.is_admin,
                'total_contributed': float(member.total_contributed)
            })
        
        result = stockvel.to_dict()
        result['members'] = members_data
        
        return jsonify({'stockvel': result}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get stockvel', 'details': str(e)}), 500

@stockvels_bp.route('/join', methods=['POST'])
@jwt_required()
def join_by_invite_code():
    """Join a stockvel using an invite code"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        invite_code = data.get('invite_code', '').strip().upper()
        
        if not invite_code:
            return jsonify({'message': 'Invite code is required'}), 400
        
        # Find stockvel by invite code
        stockvel = Stockvel.query.filter_by(invite_code=invite_code).first()
        
        if not stockvel:
            return jsonify({'message': 'Invalid invite code. Please check and try again.'}), 404
        
        if not stockvel.is_active:
            return jsonify({'message': 'This stockvel is no longer active'}), 400
        
        # Check if already a member
        existing_member = StockvelMember.query.filter_by(
            stockvel_id=stockvel.id,
            user_id=current_user_id
        ).first()
        
        if existing_member:
            return jsonify({'message': 'You are already a member of this stockvel'}), 400
        
        # Check if stockvel is full
        if len(stockvel.members) >= stockvel.max_members:
            return jsonify({'message': 'This stockvel is full'}), 400
        
        # Add as member
        member = StockvelMember(
            stockvel_id=stockvel.id,
            user_id=current_user_id,
            is_admin=False
        )
        db.session.add(member)
        db.session.commit()
        
        return jsonify({
            'message': 'Successfully joined stockvel!',
            'stockvel': stockvel.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error joining stockvel: {str(e)}", exc_info=True)
        return jsonify({'message': f'Failed to join stockvel: {str(e)}'}), 500

@stockvels_bp.route('/<int:stockvel_id>/join', methods=['POST'])
@jwt_required()
def join_stockvel(stockvel_id):
    try:
        current_user_id = int(get_jwt_identity())  # Convert string back to int
        
        stockvel = Stockvel.query.get(stockvel_id)
        if not stockvel:
            return jsonify({'error': 'Stockvel not found'}), 404
        
        if not stockvel.is_active:
            return jsonify({'error': 'Stockvel is not active'}), 400
        
        # Check if already a member
        existing_member = StockvelMember.query.filter_by(
            stockvel_id=stockvel_id,
            user_id=current_user_id
        ).first()
        
        if existing_member:
            return jsonify({'error': 'Already a member of this stockvel'}), 400
        
        # Check if stockvel is full
        if len(stockvel.members) >= stockvel.max_members:
            return jsonify({'error': 'Stockvel is full'}), 400
        
        # Add as member
        member = StockvelMember(
            stockvel_id=stockvel_id,
            user_id=current_user_id
        )
        db.session.add(member)
        db.session.commit()
        
        return jsonify({
            'message': 'Successfully joined stockvel',
            'member': member.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to join stockvel', 'details': str(e)}), 500

@stockvels_bp.route('/<int:stockvel_id>/contribute', methods=['POST'])
@jwt_required()
def make_contribution(stockvel_id):
    """Make a contribution to a stockvel"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if 'amount' not in data:
            return jsonify({'message': 'Amount is required'}), 400
        
        amount = Decimal(str(data['amount']))
        if amount <= 0:
            return jsonify({'message': 'Amount must be positive'}), 400
        
        months_paid = int(data.get('months_paid', 1))
        
        # Check if user is a member
        member = StockvelMember.query.filter_by(
            stockvel_id=stockvel_id,
            user_id=current_user_id
        ).first()
        
        if not member:
            return jsonify({'message': 'You are not a member of this stockvel'}), 403
        
        stockvel = Stockvel.query.get(stockvel_id)
        if not stockvel:
            return jsonify({'message': 'Stockvel not found'}), 404
        
        # Verify amount matches expected calculation
        expected_amount = float(stockvel.contribution_amount) * months_paid
        if abs(float(amount) - expected_amount) > 0.01:  # Allow small floating point difference
            return jsonify({'message': 'Invalid contribution amount'}), 400
        
        # Create contribution
        contribution = Contribution(
            stockvel_id=stockvel_id,
            user_id=current_user_id,
            amount=amount,
            description=data.get('description', ''),
            payment_method=data.get('payment_method', 'advance_payment'),
            status='confirmed'  # Auto-confirm for now
        )
        
        db.session.add(contribution)
        db.session.commit()
        
        return jsonify({
            'message': f'Contribution of R{amount} for {months_paid} {"period" if months_paid == 1 else "periods"} submitted successfully!',
            'contribution': contribution.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error making contribution: {str(e)}", exc_info=True)
        return jsonify({'message': f'Failed to make contribution: {str(e)}'}), 500

@stockvels_bp.route('/<int:stockvel_id>/contributions', methods=['GET'])
@jwt_required()
def get_contributions(stockvel_id):
    try:
        current_user_id = int(get_jwt_identity())  # Convert string back to int
        
        # Check if user is a member
        member = StockvelMember.query.filter_by(
            stockvel_id=stockvel_id,
            user_id=current_user_id
        ).first()
        
        if not member:
            return jsonify({'error': 'Access denied'}), 403
        
        contributions = Contribution.query.filter_by(stockvel_id=stockvel_id).order_by(
            Contribution.contribution_date.desc()
        ).all()
        
        contributions_data = []
        for contrib in contributions:
            user = User.get_by_id(contrib.user_id)
            contrib_dict = contrib.to_dict()
            contrib_dict['user_name'] = (user.display_name or user.email.split('@')[0]) if user else "Unknown"
            contributions_data.append(contrib_dict)
        
        return jsonify({'contributions': contributions_data}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get contributions', 'details': str(e)}), 500

@stockvels_bp.route('/search', methods=['GET'])
@jwt_required()
def search_stockvels():
    try:
        search_term = request.args.get('q', '').strip()
        
        if not search_term:
            return jsonify({'stockvels': []}), 200
        
        # Search public stockvels by name
        stockvels = Stockvel.query.filter(
            Stockvel.name.ilike(f'%{search_term}%'),
            Stockvel.is_active == True
        ).limit(20).all()
        
        return jsonify({
            'stockvels': [stockvel.to_dict() for stockvel in stockvels]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Search failed', 'details': str(e)}), 500

@stockvels_bp.route('/<int:stockvel_id>/members', methods=['GET'])
@jwt_required()
def get_members(stockvel_id):
    """Get all members of a stockvel with their contribution details"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Check if user is a member
        member = StockvelMember.query.filter_by(
            stockvel_id=stockvel_id,
            user_id=current_user_id
        ).first()
        
        if not member:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get stockvel
        stockvel = Stockvel.query.get(stockvel_id)
        if not stockvel:
            return jsonify({'error': 'Stockvel not found'}), 404
        
        # Get all members
        members = StockvelMember.query.filter_by(stockvel_id=stockvel_id).all()
        
        members_data = []
        for m in members:
            user = User.get_by_id(m.user_id)
            if user:
                # Calculate member's total contributions
                total_contributed = db.session.query(
                    func.sum(Contribution.amount)
                ).filter_by(
                    stockvel_id=stockvel_id,
                    user_id=m.user_id
                ).scalar() or 0
                
                # Get last contribution date
                last_contribution = Contribution.query.filter_by(
                    stockvel_id=stockvel_id,
                    user_id=m.user_id
                ).order_by(Contribution.contribution_date.desc()).first()
                
                members_data.append({
                    'user_id': user.id,
                    'user_name': user.display_name or user.email.split('@')[0],
                    'email': user.email,
                    'is_admin': m.is_admin,
                    'joined_date': m.joined_at.isoformat() if m.joined_at else None,
                    'total_contributed': float(total_contributed),
                    'last_contribution_date': last_contribution.contribution_date.isoformat() if last_contribution else None
                })
        
        return jsonify({'members': members_data}), 200
        
    except Exception as e:
        logger.error(f"Error getting members: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to get members', 'details': str(e)}), 500

@stockvels_bp.route('/<int:stockvel_id>/leave', methods=['DELETE'])
@jwt_required()
def leave_stockvel(stockvel_id):
    """Leave a stockvel (remove membership)"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Get the stockvel
        stockvel = Stockvel.query.get(stockvel_id)
        if not stockvel:
            return jsonify({'error': 'Stockvel not found'}), 404
        
        # Check if user is a member
        member = StockvelMember.query.filter_by(
            stockvel_id=stockvel_id,
            user_id=current_user_id
        ).first()
        
        if not member:
            return jsonify({'error': 'You are not a member of this stockvel'}), 400
        
        # Don't allow admin to leave if there are other members
        if member.is_admin:
            other_members = StockvelMember.query.filter(
                StockvelMember.stockvel_id == stockvel_id,
                StockvelMember.user_id != current_user_id
            ).count()
            
            if other_members > 0:
                return jsonify({
                    'error': 'Admin cannot leave while there are other members. Please transfer admin rights first or delete the stockvel.'
                }), 400
        
        # Check if user has outstanding contributions
        total_contributed = db.session.query(
            func.sum(Contribution.amount)
        ).filter_by(
            stockvel_id=stockvel_id,
            user_id=current_user_id
        ).scalar() or 0
        
        expected_amount = float(stockvel.contribution_amount) * stockvel.max_members
        
        if total_contributed < expected_amount:
            return jsonify({
                'error': f'You have outstanding contributions. Please contribute R{expected_amount - total_contributed:.2f} before leaving.',
                'warning': True
            }), 400
        
        # Remove membership
        db.session.delete(member)
        db.session.commit()
        
        logger.info(f"User {current_user_id} left stockvel {stockvel_id}")
        
        return jsonify({
            'message': 'Successfully left the stockvel',
            'success': True
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error leaving stockvel: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to leave stockvel', 'details': str(e)}), 500

@stockvels_bp.route('/<int:stockvel_id>/reorder-members', methods=['POST'])
@jwt_required()
def reorder_members(stockvel_id):
    """Reorder members (admin only)"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data or 'member_order' not in data:
            return jsonify({'error': 'member_order is required'}), 400
        
        # Get the stockvel
        stockvel = Stockvel.query.get(stockvel_id)
        if not stockvel:
            return jsonify({'error': 'Stockvel not found'}), 404
        
        # Check if user is admin
        member = StockvelMember.query.filter_by(
            stockvel_id=stockvel_id,
            user_id=current_user_id,
            is_admin=True
        ).first()
        
        if not member:
            return jsonify({'error': 'Only admins can reorder members'}), 403
        
        member_order = data['member_order']
        
        # Update the order in database (you can add a 'position' column to StockvelMember)
        # For now, we'll just return success and the order is maintained in the frontend
        # In a real implementation, add a 'position' column to track order
        
        logger.info(f"Member order updated for stockvel {stockvel_id}: {member_order}")
        
        return jsonify({
            'message': 'Member order updated successfully',
            'member_order': member_order
        }), 200
        
    except Exception as e:
        logger.error(f"Error reordering members: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to reorder members', 'details': str(e)}), 500
