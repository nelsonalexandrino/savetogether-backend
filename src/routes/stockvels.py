from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.stockvel import Stockvel, StockvelMember, Contribution
from models.user import User
from services.database_service import db
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
        
        return jsonify({
            'stockvels': [stockvel.to_dict() for stockvel in user_stockvels]
        }), 200
        
    except Exception as e:
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
    try:
        current_user_id = int(get_jwt_identity())  # Convert string back to int
        data = request.get_json()
        
        if 'amount' not in data:
            return jsonify({'error': 'Amount is required'}), 400
        
        amount = Decimal(str(data['amount']))
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
        
        # Check if user is a member
        member = StockvelMember.query.filter_by(
            stockvel_id=stockvel_id,
            user_id=current_user_id
        ).first()
        
        if not member:
            return jsonify({'error': 'You are not a member of this stockvel'}), 403
        
        stockvel = Stockvel.query.get(stockvel_id)
        if not stockvel:
            return jsonify({'error': 'Stockvel not found'}), 404
        
        # Create contribution
        contribution = Contribution(
            stockvel_id=stockvel_id,
            user_id=current_user_id,
            amount=amount,
            description=data.get('description', '')
        )
        
        # Update member total contribution
        member.total_contributed += amount
        
        # Update stockvel current amount
        stockvel.current_amount += amount
        
        db.session.add(contribution)
        db.session.commit()
        
        return jsonify({
            'message': 'Contribution made successfully',
            'contribution': contribution.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to make contribution', 'details': str(e)}), 500

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
            contrib_dict['user'] = user.to_dict() if user else None
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