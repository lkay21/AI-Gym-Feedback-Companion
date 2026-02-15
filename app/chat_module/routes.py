"""
API routes for chatbot functionality
"""
from flask import Blueprint, request, jsonify, session
from typing import Dict, Any, Optional, Tuple
from app.chat_module.gemini_client import GeminiClient
from app.fitness.plan_transformer import mapLLMPlanToStructuredPlan, PlanParseError

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')


def get_authenticated_user_id() -> Optional[str]:
    """Get authenticated user ID from session"""
    return session.get('user_id')


def validate_chat_request(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate chat API request"""
    if not data:
        return False, "Request body is required"
    
    message = data.get('message', '').strip()
    if not message:
        return False, "Message is required and cannot be empty"
    
    if len(message) > 2000:
        return False, "Message is too long (max 2000 characters)"
    
    return True, None


def validate_plan_request(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate plan generation request"""
    is_valid, error_msg = validate_chat_request(data)
    if not is_valid:
        return is_valid, error_msg

    start_date = data.get('startDate', '').strip() if isinstance(data, dict) else ''
    if not start_date:
        return False, "startDate is required"

    return True, None


@chat_bp.route('', methods=['POST'])
def chat():
    """
    Main chat endpoint - generates AI response to user message
    
    Request body:
    {
        "message": "user's question or message",
        "conversation_history": [  // optional
            {"role": "user", "content": "previous message"},
            {"role": "assistant", "content": "previous response"}
        ],
        "profile": {  // optional
            "name": "...",
            "age": 25,
            "height": "175cm",
            "weight": "70kg",
            "fitness_goals": ["lose weight", "build muscle"],
            "activity_level": "moderate"
        }
    }
    
    Response:
    {
        "response": "AI generated response",
        "success": true
    }
    """
    try:
        # Check authentication (optional - can be made required)
        user_id = get_authenticated_user_id()
        
        # Validate request
        data = request.get_json()
        is_valid, error_msg = validate_chat_request(data)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        message = data.get('message', '').strip()
        conversation_history = data.get('conversation_history', [])
        user_profile = data.get('profile', {})
        
        # Initialize Gemini client
        try:
            gemini_client = GeminiClient()
        except ValueError as e:
            return jsonify({
                'error': 'AI service is not configured properly',
                'details': str(e)
            }), 500
        
        # Generate AI response
        try:
            response_text = gemini_client.generate_response(
                user_message=message,
                conversation_history=conversation_history,
                user_profile=user_profile
            )
            
            return jsonify({
                'response': response_text,
                'success': True
            }), 200
            
        except Exception as e:
            error_message = str(e)
            return jsonify({
                'error': 'Failed to generate AI response',
                'details': error_message
            }), 500
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'An unexpected error occurred',
            'details': str(e)
        }), 500


@chat_bp.route('/plan', methods=['POST'])
def generate_plan():
    """
    Generate a structured fitness plan from the LLM response.

    Request body:
    {
        "message": "prompt to generate plan",
        "conversation_history": [],
        "profile": {},
        "startDate": "YYYY-MM-DD"
    }
    """
    try:
        data = request.get_json()
        is_valid, error_msg = validate_plan_request(data)
        if not is_valid:
            return jsonify({'error': error_msg}), 400

        message = data.get('message', '').strip()
        conversation_history = data.get('conversation_history', [])
        user_profile = data.get('profile', {})
        start_date = data.get('startDate')

        try:
            gemini_client = GeminiClient()
        except ValueError as e:
            return jsonify({
                'error': 'AI service is not configured properly',
                'details': str(e)
            }), 500

        try:
            response_text = gemini_client.generate_response(
                user_message=message,
                conversation_history=conversation_history,
                user_profile=user_profile
            )

            structured_plan = mapLLMPlanToStructuredPlan(response_text, start_date)

            return jsonify({
                'response': response_text,
                'structuredPlan': structured_plan,
                'success': True
            }), 200
        except PlanParseError as e:
            return jsonify({
                'error': 'Failed to parse fitness plan',
                'details': str(e)
            }), 500
        except Exception as e:
            return jsonify({
                'error': 'Failed to generate fitness plan',
                'details': str(e)
            }), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'An unexpected error occurred',
            'details': str(e)
        }), 500


@chat_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for chat service"""
    try:
        # Try to initialize Gemini client to verify configuration
        gemini_client = GeminiClient()
        return jsonify({
            'status': 'healthy',
            'service': 'chat',
            'model': gemini_client.model_name,
            'configured': True
        }), 200
    except ValueError as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'chat',
            'configured': False,
            'error': str(e)
        }), 503
    except Exception as e:
        return jsonify({
            'status': 'error',
            'service': 'chat',
            'error': str(e)
        }), 500

