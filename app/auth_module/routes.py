from flask import Blueprint, request, jsonify, session
from .supabase_client import get_supabase_client
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, None

def validate_username(username):
    """Validate username"""
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    # Check if username contains only allowed characters (letters, numbers, underscores, hyphens)
    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-')
    if not all(c in allowed_chars for c in username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    return True, None

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

        # Validate username
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            return jsonify({'error': error_msg}), 400

        # Validate email
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400

        # Validate password
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({'error': error_msg}), 400

        # Get Supabase client
        try:
            supabase = get_supabase_client()
        except ValueError as e:
            # Supabase credentials not configured
            print(f"Supabase configuration error: {str(e)}")
            return jsonify({'error': 'Server configuration error. Please contact administrator.'}), 500
        except Exception as e:
            print(f"Supabase client error: {str(e)}")
            return jsonify({'error': 'Server configuration error. Please contact administrator.'}), 500

        # Sign up user with Supabase
        # Store username in user metadata
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "username": username
                },
                "email_confirm": False  # Set to True if email confirmation is required
            }
        })

        if response.user:
            # Check if email confirmation is required
            if response.session:
                # Email confirmed, user can log in immediately
                session['access_token'] = response.session.access_token
                session['refresh_token'] = response.session.refresh_token
                session['user_id'] = response.user.id
                session['email'] = response.user.email
                session['username'] = username
                session.permanent = True

                return jsonify({
                    'message': 'User registered successfully',
                    'user': {
                        'id': response.user.id,
                        'email': response.user.email,
                        'username': username,
                        'created_at': response.user.created_at
                    }
                }), 201
            else:
                # Email confirmation required
                return jsonify({
                    'message': 'Registration successful. Please check your email to confirm your account.',
                    'user': {
                        'id': response.user.id,
                        'email': response.user.email,
                        'username': username,
                        'email_confirmed': False
                    }
                }), 201
        else:
            return jsonify({'error': 'Registration failed'}), 500

    except Exception as e:
        error_message = str(e)
        # Handle Supabase-specific errors
        if 'User already registered' in error_message or 'already registered' in error_message.lower():
            return jsonify({'error': 'Email already registered'}), 400
        elif 'Password' in error_message:
            return jsonify({'error': 'Password does not meet requirements'}), 400
        
        import traceback
        print(f"Registration error: {error_message}")
        traceback.print_exc()
        return jsonify({'error': f'Registration failed: {error_message}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        username_or_email = data.get('username', '').strip()
        password = data.get('password', '')

        if not username_or_email or not password:
            return jsonify({'error': 'Username/email and password are required'}), 400

        # Get Supabase client
        try:
            supabase = get_supabase_client()
        except ValueError as e:
            # Supabase credentials not configured
            return jsonify({'error': 'Server configuration error. Please contact administrator.'}), 500
        except Exception as e:
            import traceback
            print(f"Supabase client error: {str(e)}")
            traceback.print_exc()
            return jsonify({'error': 'Server configuration error. Please contact administrator.'}), 500

        # Supabase uses email for login, so if username is provided, we need to look it up
        # For now, assume the input is email (we can enhance this later with a username lookup table)
        email = username_or_email.lower() if '@' in username_or_email else username_or_email

        # Sign in with Supabase
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
        except Exception as supabase_error:
            error_msg = str(supabase_error)
            # Check for specific Supabase errors
            if 'Invalid login credentials' in error_msg or 'invalid' in error_msg.lower():
                # Expected error - don't print full traceback
                return jsonify({'error': 'Invalid email or password'}), 401
            elif 'Email not confirmed' in error_msg:
                return jsonify({'error': 'Please confirm your email before logging in'}), 401
            else:
                # Unexpected error - log it
                import traceback
                print(f"Login error: {error_msg}")
                traceback.print_exc()
                return jsonify({'error': 'Login failed. Please try again.'}), 500

        if response.user and response.session:
            # Get username from user metadata
            username = response.user.user_metadata.get('username', email.split('@')[0])
            
            # Set session with Supabase tokens
            session['access_token'] = response.session.access_token
            session['refresh_token'] = response.session.refresh_token
            session['user_id'] = response.user.id
            session['email'] = response.user.email
            session['username'] = username
            session.permanent = True

            return jsonify({
                'message': 'Login successful',
                'user': {
                    'id': response.user.id,
                    'email': response.user.email,
                    'username': username,
                    'created_at': response.user.created_at
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401

    except Exception as e:
        error_message = str(e)
        # Handle Supabase-specific errors
        if 'Invalid login credentials' in error_message or 'invalid' in error_message.lower():
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Unexpected error - log it
        import traceback
        print(f"Login error: {error_message}")
        traceback.print_exc()
        return jsonify({'error': 'Login failed. Please try again.'}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user and clear session"""
    try:
        # Get access token from session
        access_token = session.get('access_token')
        
        if access_token:
            # Sign out from Supabase
            supabase = get_supabase_client()
            # Set the session for this client
            supabase.auth.set_session(access_token, session.get('refresh_token'))
            supabase.auth.sign_out()
        
        # Clear Flask session
        session.clear()
        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
        # Clear session even if Supabase logout fails
        session.clear()
        return jsonify({'message': 'Logged out successfully'}), 200


@auth_bp.route('/check', methods=['GET'])
def check_session():
    """Check if user is logged in"""
    try:
        access_token = session.get('access_token')
        user_id = session.get('user_id')
        
        if access_token and user_id:
            # Verify token with Supabase
            supabase = get_supabase_client()
            supabase.auth.set_session(access_token, session.get('refresh_token'))
            user = supabase.auth.get_user(access_token)
            
            if user:
                username = user.user.user_metadata.get('username', session.get('username', ''))
                return jsonify({
                    'logged_in': True,
                    'user': {
                        'id': user.user.id,
                        'email': user.user.email,
                        'username': username,
                        'created_at': user.user.created_at
                    }
                }), 200
        
        return jsonify({'logged_in': False}), 200
    except Exception as e:
        # If token is invalid, clear session
        session.clear()
        return jsonify({'logged_in': False}), 200


@auth_bp.route('/user', methods=['GET'])
def get_user():
    """Get current user info"""
    try:
        access_token = session.get('access_token')
        if not access_token:
            return jsonify({'error': 'Not authenticated'}), 401
        
        # Get user from Supabase
        supabase = get_supabase_client()
        supabase.auth.set_session(access_token, session.get('refresh_token'))
        user = supabase.auth.get_user(access_token)
        
        if not user:
            session.clear()
            return jsonify({'error': 'User not found'}), 404
        
        username = user.user.user_metadata.get('username', session.get('username', ''))
        return jsonify({
            'user': {
                'id': user.user.id,
                'email': user.user.email,
                'username': username,
                'created_at': user.user.created_at
            }
        }), 200
    except Exception as e:
        session.clear()
        return jsonify({'error': 'Not authenticated'}), 401
