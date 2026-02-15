"""
API routes for user profiles and health data
"""
from flask import Blueprint, request, jsonify, session
from typing import Dict, Any, Tuple
from datetime import datetime
from app.profile_module.service import ProfileService, HealthDataService
from app.profile_module.models import UserProfile, HealthData

profile_bp = Blueprint('profile', __name__, url_prefix='/api/profile')


def get_authenticated_user_id() -> str:
    """Get authenticated user ID from session"""
    user_id = session.get('user_id')
    if not user_id:
        raise ValueError("User not authenticated")
    return user_id


def validate_profile_data(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate profile data"""
    if 'age' in data and data['age'] is not None:
        if not isinstance(data['age'], int) or data['age'] < 1 or data['age'] > 150:
            return False, "Age must be between 1 and 150"
    
    if 'height' in data and data['height'] is not None:
        if not isinstance(data['height'], (int, float)) or data['height'] <= 0:
            return False, "Height must be a positive number"
    
    if 'weight' in data and data['weight'] is not None:
        if not isinstance(data['weight'], (int, float)) or data['weight'] <= 0:
            return False, "Weight must be a positive number"
    
    if 'fitness_goals' in data and data['fitness_goals'] is not None:
        if not isinstance(data['fitness_goals'], list):
            return False, "Fitness goals must be a list"
    
    return True, None


# User Profile Routes

@profile_bp.route('/user', methods=['GET'])
def get_profile():
    """Get current user's profile"""
    try:
        user_id = get_authenticated_user_id()
        service = ProfileService()
        profile = service.get_profile(user_id)
        
        if profile:
            return jsonify({'profile': profile.to_dict()}), 200
        else:
            return jsonify({'message': 'Profile not found', 'profile': None}), 404
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@profile_bp.route('/user', methods=['POST'])
def create_profile():
    """Create or update user profile"""
    try:
        user_id = get_authenticated_user_id()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate data
        is_valid, error_msg = validate_profile_data(data)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        service = ProfileService()
        
        # Check if profile exists
        existing_profile = service.get_profile(user_id)
        
        if existing_profile:
            # Update existing profile
            profile = service.update_profile(user_id, data)
            return jsonify({
                'message': 'Profile updated successfully',
                'profile': profile.to_dict()
            }), 200
        else:
            # Create new profile
            profile = UserProfile(
                user_id=user_id,
                age=data.get('age'),
                height=data.get('height'),
                weight=data.get('weight'),
                fitness_goals=data.get('fitness_goals', []),
                gender=data.get('gender'),
                activity_level=data.get('activity_level')
            )
            service.create_profile(profile)
            return jsonify({
                'message': 'Profile created successfully',
                'profile': profile.to_dict()
            }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@profile_bp.route('/user', methods=['PUT'])
def update_profile():
    """Update user profile (partial update)"""
    try:
        user_id = get_authenticated_user_id()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate data
        is_valid, error_msg = validate_profile_data(data)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        service = ProfileService()
        
        # Check if profile exists
        existing_profile = service.get_profile(user_id)
        if not existing_profile:
            return jsonify({'error': 'Profile not found. Create profile first.'}), 404
        
        # Update profile
        profile = service.update_profile(user_id, data)
        return jsonify({
            'message': 'Profile updated successfully',
            'profile': profile.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@profile_bp.route('/user', methods=['DELETE'])
def delete_profile():
    """Delete user profile"""
    try:
        user_id = get_authenticated_user_id()
        service = ProfileService()
        service.delete_profile(user_id)
        return jsonify({'message': 'Profile deleted successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Health Data Routes

@profile_bp.route('/health', methods=['POST'])
def create_health_data():
    """Create a new health data entry"""
    try:
        user_id = get_authenticated_user_id()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Use provided timestamp or current time
        timestamp = data.get('timestamp') or datetime.utcnow().isoformat()
        
        health_data = HealthData(
            user_id=user_id,
            timestamp=timestamp,
            # Fixed health data fields
            age=data.get('age'),
            height=data.get('height'),
            weight=data.get('weight'),
            gender=data.get('gender'),
            fitness_goal=data.get('fitness_goal'),
            # Context field for fitness-goal-specific Q&A
            context=data.get('context', {})  # Can be dict with Q&A pairs
        )
        
        service = HealthDataService()
        service.create_health_data(health_data)
        
        return jsonify({
            'message': 'Health data created successfully',
            'health_data': health_data.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@profile_bp.route('/health', methods=['GET'])
def get_health_data():
    """Get health data for current user"""
    try:
        user_id = get_authenticated_user_id()
        
        # Get query parameters
        limit = request.args.get('limit', 100, type=int)
        start_timestamp = request.args.get('start_timestamp')
        end_timestamp = request.args.get('end_timestamp')
        timestamp = request.args.get('timestamp')  # Get specific entry
        
        service = HealthDataService()
        
        if timestamp:
            # Get specific entry
            health_data = service.get_health_data(user_id, timestamp)
            if health_data:
                return jsonify({'health_data': health_data.to_dict()}), 200
            else:
                return jsonify({'message': 'Health data not found', 'health_data': None}), 404
        else:
            # Get all entries (with optional filters)
            health_data_list = service.get_user_health_data(
                user_id,
                limit=limit,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp
            )
            return jsonify({
                'health_data': [hd.to_dict() for hd in health_data_list],
                'count': len(health_data_list)
            }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@profile_bp.route('/health/<timestamp>', methods=['PUT'])
def update_health_data(timestamp):
    """Update a specific health data entry"""
    try:
        user_id = get_authenticated_user_id()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        service = HealthDataService()
        
        # Check if entry exists
        existing = service.get_health_data(user_id, timestamp)
        if not existing:
            return jsonify({'error': 'Health data entry not found'}), 404
        
        # Update entry
        updated = service.update_health_data(user_id, timestamp, data)
        
        return jsonify({
            'message': 'Health data updated successfully',
            'health_data': updated.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@profile_bp.route('/health/<timestamp>', methods=['DELETE'])
def delete_health_data(timestamp):
    """Delete a specific health data entry"""
    try:
        user_id = get_authenticated_user_id()
        service = HealthDataService()
        service.delete_health_data(user_id, timestamp)
        return jsonify({'message': 'Health data deleted successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

