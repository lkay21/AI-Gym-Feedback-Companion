"""
API routes for user profiles and health data
"""
import json
from flask import Blueprint, request, jsonify, session
from typing import Dict, Any
from datetime import datetime
from app.profile_module.service import ProfileService, HealthDataService
from app.profile_module.models import UserProfile, HealthData
from app.core.errors import AppError, ValidationError, UnauthorizedError, NotFoundError, DatabaseError

profile_bp = Blueprint('profile', __name__, url_prefix='/api/profile')


def get_authenticated_user_id() -> str:
    """Get authenticated user ID from session"""
    user_id = session.get('user_id')
    if not user_id:
        raise UnauthorizedError("User not authenticated")
    return user_id


# User Profile Routes (profile = user_id only; all health data is in HealthData)

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
            raise NotFoundError("Profile not found")
    except AppError:
        raise
    except ValueError as e:
        raise UnauthorizedError(str(e))
    except Exception as e:
        raise DatabaseError("Failed to fetch profile") from e


@profile_bp.route('/user', methods=['POST'])
def create_profile():
    """Ensure user profile exists (profile = user_id only). Health data lives in /api/profile/health."""
    try:
        user_id = get_authenticated_user_id()
        service = ProfileService()
        existing = service.get_profile(user_id)
        if existing:
            return jsonify({'message': 'Profile exists', 'profile': existing.to_dict()}), 200
        service.create_profile(UserProfile(user_id=user_id))
        profile = service.get_profile(user_id)
        return jsonify({'message': 'Profile created', 'profile': profile.to_dict()}), 201
    except AppError:
        raise
    except ValueError as e:
        raise UnauthorizedError(str(e))
    except Exception as e:
        raise DatabaseError("Failed to create profile") from e


@profile_bp.route('/user', methods=['PUT'])
def update_profile():
    """No fields to update (profile = user_id only). Ensures profile exists."""
    try:
        user_id = get_authenticated_user_id()
        service = ProfileService()
        profile = service.update_profile(user_id, request.get_json() or {})
        return jsonify({'message': 'Profile OK', 'profile': profile.to_dict()}), 200
    except AppError:
        raise
    except ValueError as e:
        raise UnauthorizedError(str(e))
    except Exception as e:
        raise DatabaseError("Failed to update profile") from e


@profile_bp.route('/user', methods=['DELETE'])
def delete_profile():
    """Delete user profile"""
    try:
        user_id = get_authenticated_user_id()
        service = ProfileService()
        service.delete_profile(user_id)
        return jsonify({'message': 'Profile deleted successfully'}), 200
    except AppError:
        raise
    except ValueError as e:
        raise UnauthorizedError(str(e))
    except Exception as e:
        raise DatabaseError("Failed to delete profile") from e


# Health Data Routes

@profile_bp.route('/health', methods=['POST'])
def create_health_data():
    """Create a new health data entry"""
    try:
        user_id = get_authenticated_user_id()
        data = request.get_json()
        
        if not data:
            raise ValidationError("No data provided")
        
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
    except AppError:
        raise
    except ValueError as e:
        raise UnauthorizedError(str(e))
    except Exception as e:
        raise DatabaseError("Failed to create health data") from e


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
                raise NotFoundError("Health data not found")
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
    except AppError:
        raise
    except ValueError as e:
        raise UnauthorizedError(str(e))
    except Exception as e:
        raise DatabaseError("Failed to fetch health data") from e


@profile_bp.route('/health/<timestamp>', methods=['PUT'])
def update_health_data(timestamp):
    """Update a specific health data entry"""
    try:
        user_id = get_authenticated_user_id()
        data = request.get_json()
        
        if not data:
            raise ValidationError("No data provided")
        if 'context' in data and isinstance(data['context'], dict):
            data = {**data, 'context': json.dumps(data['context'])}
        
        service = HealthDataService()
        existing = service.get_health_data(user_id, timestamp)
        if not existing:
            raise NotFoundError("Health data entry not found")
        updated = service.update_health_data(user_id, timestamp, data)
        
        return jsonify({
            'message': 'Health data updated successfully',
            'health_data': updated.to_dict()
        }), 200
    except AppError:
        raise
    except ValueError as e:
        raise UnauthorizedError(str(e))
    except Exception as e:
        raise DatabaseError("Failed to update health data") from e


@profile_bp.route('/health/<timestamp>', methods=['DELETE'])
def delete_health_data(timestamp):
    """Delete a specific health data entry"""
    try:
        user_id = get_authenticated_user_id()
        service = HealthDataService()
        service.delete_health_data(user_id, timestamp)
        return jsonify({'message': 'Health data deleted successfully'}), 200
    except AppError:
        raise
    except ValueError as e:
        raise UnauthorizedError(str(e))
    except Exception as e:
        raise DatabaseError("Failed to delete health data") from e

