from flask import Blueprint, request, jsonify, session
from app.db_instance import db
from .models import User
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        # Validation
        if not username or not email or not password:
            return jsonify({'error': 'Username, email, and password are required'}), 400

        # Validate email
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400

        # Validate password
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400

        # Check if email already exists (if User model has email field)
        if hasattr(User, 'email'):
            if User.query.filter_by(email=email).first():
                return jsonify({'error': 'Email already registered'}), 400
            new_user = User(username=username, email=email)
        else:
            new_user = User(username=username)

        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Set session
        session['user_id'] = new_user.id
        session['username'] = new_user.username
        session.permanent = True

        user_data = {
            'id': new_user.id,
            'username': new_user.username
        }
        if hasattr(new_user, 'email'):
            user_data['email'] = new_user.email

        return jsonify({
            'message': 'User registered successfully',
            'user': user_data
        }), 201

    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Registration error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Registration failed. Please try again.'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        username_or_email = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not password:
            return jsonify({'error': 'Password is required'}), 400

        # Try to find user by username or email
        user = None
        if username_or_email:
            user = User.query.filter_by(username=username_or_email).first()
        
        # If not found by username and email field exists, try email
        if not user and email and hasattr(User, 'email'):
            user = User.query.filter_by(email=email).first()
        elif not user and username_or_email and '@' in username_or_email and hasattr(User, 'email'):
            # If username looks like email, try that
            user = User.query.filter_by(email=username_or_email.lower()).first()

        if user and user.check_password(password):
            # Set session
            session['user_id'] = user.id
            session['username'] = user.username
            session.permanent = True

            user_data = {
                'id': user.id,
                'username': user.username
            }
            if hasattr(user, 'email'):
                user_data['email'] = user.email

            return jsonify({
                'message': 'Login successful',
                'user': user_data
            }), 200
        else:
            return jsonify({'error': 'Invalid username/email or password'}), 401

    except Exception as e:
        import traceback
        print(f"Login error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Login failed. Please try again.'}), 500
