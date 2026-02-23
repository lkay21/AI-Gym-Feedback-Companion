"""
API routes for chatbot functionality
"""
from flask import Blueprint, request, jsonify, session
from typing import Dict, Any, Optional, Tuple
from datetime import date
from app.chatbot.llm_service import generate_llm_response, validateFitnessPlanSchema
from app.fitness.plan_transformer import mapLLMPlanToStructuredPlan, mapDatabasePlanToCalendar
from app.fitness_plan_module.service import FitnessPlanService
from app.core.errors import AppError, ValidationError, UnauthorizedError, NotFoundError, DatabaseError

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


def validate_init_plan_request(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate init plan request payload"""
    if not data:
        return False, "Request body is required"

    required_fields = ["userId", "fitnessGoals", "experienceLevel", "availability"]
    for field in required_fields:
        if field not in data:
            return False, f"{field} is required"

    return True, None


def build_init_plan_prompt(payload: Dict[str, Any]) -> str:
    """Construct the fitness plan prompt for LLM"""
    fitness_goals = payload.get("fitnessGoals")
    experience_level = payload.get("experienceLevel")
    availability = payload.get("availability")

    return (
        "Create a structured fitness plan in valid JSON only. "
        "Include planName, weeks, days with workoutType and exercises. "
        f"Fitness goals: {fitness_goals}. "
        f"Experience level: {experience_level}. "
        f"Availability: {availability}."
    )


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
            raise ValidationError(error_msg)
        
        message = data.get('message', '').strip()
        conversation_history = data.get('conversation_history', [])
        user_profile = data.get('profile', {})
        
        # Generate AI response
        result = generate_llm_response(
            prompt=message,
            context=conversation_history,
            metadata={"profile": user_profile},
        )

        if result["success"]:
            return jsonify(result), 200

        raise DatabaseError(result.get("error") or "Failed to generate response")
        
    except AppError:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise DatabaseError("An unexpected error occurred") from e


@chat_bp.route('/init', methods=['POST'])
def init_plan():
    """Initialize and retrieve the 2-week fitness plan from DynamoDB"""
    try:
        user_id = get_authenticated_user_id()
        if not user_id:
            raise UnauthorizedError("Not authenticated")

        # Retrieve the 2-week fitness plan from DynamoDB
        fp_svc = FitnessPlanService()
        plan_objects = fp_svc.get_by_user(user_id)
        
        if not plan_objects:
            raise NotFoundError("No fitness plan found for user. Generate a plan first.")
        
        # Convert FitnessPlan objects to dictionaries
        plan_entries = [plan.to_dict() for plan in plan_objects]
        
        # Transform to calendar format
        structured_plan = mapDatabasePlanToCalendar(plan_entries)

        return jsonify({
            'success': True,
            'data': structured_plan
        }), 200
    except AppError:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise DatabaseError("An unexpected error occurred") from e


@chat_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for chat service"""
    try:
        # Verify OpenAI configuration
        from os import getenv
        api_key = getenv("OPENAI_API_KEY")
        model_name = getenv("MODEL_NAME", "gpt-4o-mini")
        if not api_key:
            raise DatabaseError("OPENAI_API_KEY is not set in environment variables")
        return jsonify({
            'status': 'healthy',
            'service': 'chat',
            'model': model_name,
            'configured': True
        }), 200
    except AppError:
        raise
    except Exception as e:
        raise DatabaseError("An unexpected error occurred") from e


@chat_bp.route('/health/llm', methods=['GET'])
def llm_health_check():
    """Health check endpoint for LLM service"""
    try:
        from os import getenv
        api_key = getenv("OPENAI_API_KEY")
        model_name = getenv("MODEL_NAME", "gpt-4o-mini")
        if not api_key:
            raise DatabaseError("OPENAI_API_KEY is not set")
        return jsonify({
            'status': 'healthy',
            'service': 'llm',
            'configured': True,
            'model': model_name
        }), 200
    except AppError:
        raise
    except Exception as e:
        raise DatabaseError("An unexpected error occurred") from e