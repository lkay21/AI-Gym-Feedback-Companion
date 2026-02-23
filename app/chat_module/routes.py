"""
API routes for chatbot functionality
"""
import re
from flask import Blueprint, request, jsonify, session
from typing import Dict, Any, Optional, Tuple, List
from app.chat_module.gemini_client import GeminiClient
from app.fitness.plan_transformer import mapLLMPlanToStructuredPlan, PlanParseError
from app.profile_module.service import HealthDataService

chat_bp = Blueprint('chat', __name__)

# Order of fixed characteristics we collect before fitness goal
FIXED_FIELD_QUESTIONS = [
    ("age", "What is your age? (years)"),
    ("height", "What is your height? (e.g. 175 cm or 5 ft 10 in)"),
    ("weight", "What is your weight? (e.g. 70 kg or 154 lbs)"),
    ("gender", "What is your gender?"),
]


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


def _parse_health_context(context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Normalize health profile context (pending_fixed, qa_pairs, pending_questions)."""
    if not context:
        return {
            "pending_fixed": list(f[0] for f in FIXED_FIELD_QUESTIONS),
            "qa_pairs": [],
            "pending_questions": [],
        }
    pending_fixed = context.get("pending_fixed")
    if not isinstance(pending_fixed, list):
        pending_fixed = list(f[0] for f in FIXED_FIELD_QUESTIONS)
    return {
        "pending_fixed": pending_fixed,
        "qa_pairs": context.get("qa_pairs") or [],
        "pending_questions": context.get("pending_questions") or [],
    }


def _parse_fixed_value(field: str, message: str) -> Optional[Any]:
    """Parse user message into value for the given fixed field. Returns None if unparseable."""
    msg = message.strip()
    if not msg:
        return None
    if field == "age":
        m = re.search(r"\d+", msg)
        if m:
            v = int(m.group())
            if 1 <= v <= 120:
                return v
        return None
    if field == "height":
        # Try "5 ft 10 in" or "5 10" (ft in) first
        m_ft_in = re.search(r"(\d{1,2})\s*(?:ft|feet|')?\s*(\d{0,2})\s*(?:in|inches|''|\")?", msg, re.I)
        if m_ft_in:
            ft = int(m_ft_in.group(1))
            in_part = int(m_ft_in.group(2)) if (m_ft_in.group(2) or "").strip() else 0
            if 3 <= ft <= 8 and 0 <= in_part <= 11:
                return round(ft * 30.48 + in_part * 2.54, 1)  # store in cm
        # Two numbers only, e.g. "5 10"
        nums = re.findall(r"\d+\.?\d*", msg)
        if len(nums) >= 2:
            a, b = int(float(nums[0])), int(float(nums[1]))
            if 3 <= a <= 8 and 0 <= b <= 11:
                return round(a * 30.48 + b * 2.54, 1)
        # Single number + optional unit (cm)
        m = re.search(r"(\d+\.?\d*)\s*(cm|ft)?", msg, re.I)
        if m:
            val = float(m.group(1))
            if m.group(2) and (m.group(2) or "").lower() == "ft":
                val = val * 30.48
            return round(val, 1) if val < 300 else val  # assume cm if large
        return None
    if field == "weight":
        m = re.search(r"(\d+\.?\d*)\s*(kg|lbs|lb)?", msg, re.I)
        if m:
            return float(m.group(1))
        return None
    if field == "gender":
        return msg[:100] if msg else None
    return None


@chat_bp.route('/health-onboarding', methods=['POST'])
def health_onboarding():
    """
    Health onboarding: ask fixed characteristics (age, height, weight, gender) → fitness goal
    → 2-3 AI follow-up questions → store all in HealthData.
    """
    try:
        user_id = get_authenticated_user_id()
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401

        data = request.get_json() or {}
        message = (data.get('message') or '').strip()
        if len(message) > 2000:
            return jsonify({'error': 'Message too long'}), 400

        health_svc = HealthDataService()
        health_profile = health_svc.get_health_profile(user_id)
        ctx = _parse_health_context(getattr(health_profile, 'context', None) if health_profile else None)
        pending_fixed = list(ctx.get("pending_fixed", []))
        # If we already have all fixed fields, don't re-ask; clear pending_fixed in DB
        if health_profile and pending_fixed:
            has_all = (
                getattr(health_profile, 'age', None) is not None
                and getattr(health_profile, 'height', None) is not None
                and getattr(health_profile, 'weight', None) is not None
                and getattr(health_profile, 'gender', None)
            )
            if has_all:
                pending_fixed = []
                ctx["pending_fixed"] = []
                health_svc.create_or_update_health_profile(
                    user_id,
                    context={"pending_fixed": [], "qa_pairs": ctx.get("qa_pairs", []), "pending_questions": ctx.get("pending_questions", [])},
                )

        try:
            gemini = GeminiClient()
        except ValueError as e:
            return jsonify({'error': 'AI service not configured', 'details': str(e)}), 500

        # ---- Phase: ask_fixed (collect age, height, weight, gender) ----
        if pending_fixed:
            current_field = pending_fixed[0]
            question_for = dict(FIXED_FIELD_QUESTIONS).get(current_field, f"What is your {current_field}?")

            if not message:
                if not health_profile:
                    health_svc.create_or_update_health_profile(
                        user_id,
                        context={"pending_fixed": pending_fixed, "qa_pairs": [], "pending_questions": []},
                    )
                return jsonify({
                    'response': "I'd like to tailor advice to you. " + question_for,
                    'phase': 'ask_fixed',
                    'success': True,
                }), 200

            value = _parse_fixed_value(current_field, message)
            if value is None:
                return jsonify({
                    'response': "I couldn't parse that. " + question_for,
                    'phase': 'ask_fixed',
                    'success': True,
                }), 200

            context_obj = {"pending_fixed": pending_fixed[1:], "qa_pairs": ctx.get("qa_pairs", []), "pending_questions": ctx.get("pending_questions", [])}
            kwargs = {"context": context_obj}
            if current_field == "age":
                kwargs["age"] = value
            elif current_field == "height":
                kwargs["height"] = value
            elif current_field == "weight":
                kwargs["weight"] = value
            elif current_field == "gender":
                kwargs["gender"] = value
            health_svc.create_or_update_health_profile(user_id, **kwargs)

            next_pending = pending_fixed[1:]
            if not next_pending:
                return jsonify({
                    'response': "Thanks! What is your main fitness goal right now? (e.g. lose weight, build muscle, improve endurance)",
                    'phase': 'ask_goal',
                    'success': True,
                }), 200
            next_question = dict(FIXED_FIELD_QUESTIONS).get(next_pending[0], f"What is your {next_pending[0]}?")
            return jsonify({
                'response': next_question,
                'phase': 'ask_fixed',
                'success': True,
            }), 200

        # ---- Phase: ask_goal (then follow_up) ----
        fitness_goal = getattr(health_profile, 'fitness_goal', None) if health_profile else None
        if not fitness_goal:
            if not message:
                intro = gemini.build_fixed_stats_intro(health_profile.to_dict() if health_profile else {})
                return jsonify({
                    'response': intro,
                    'phase': 'ask_goal',
                    'success': True,
                }), 200
            fitness_goal = message
            questions = gemini.generate_follow_up_questions(fitness_goal, count=3)
            context_obj = {"pending_fixed": [], "qa_pairs": [], "pending_questions": questions}
            health_svc.create_or_update_health_profile(user_id, fitness_goal=fitness_goal, context=context_obj)
            first_q = questions[0] if questions else "Is there anything else you'd like me to know?"
            return jsonify({
                'response': first_q,
                'phase': 'follow_up',
                'success': True,
            }), 200

        # ---- Phase: follow_up (Q&A) ----
        qa_pairs = list(ctx.get("qa_pairs", []))
        pending = list(ctx.get("pending_questions", []))

        if not message and pending:
            return jsonify({'response': pending[0], 'phase': 'follow_up', 'success': True}), 200

        if message and pending:
            current_q = pending.pop(0)
            qa_pairs.append({"q": current_q, "a": message})
            context_obj = {"pending_fixed": [], "qa_pairs": qa_pairs, "pending_questions": pending}
            health_svc.create_or_update_health_profile(user_id, context=context_obj)
            if pending:
                return jsonify({'response': pending[0], 'phase': 'follow_up', 'success': True}), 200
            return jsonify({
                'response': "Thanks! I've saved your answers. Ask me for personalized workout or nutrition advice anytime.",
                'phase': 'complete',
                'success': True,
            }), 200

        return jsonify({
            'response': "Your health profile is already set up. What would you like help with today?",
            'phase': 'complete',
            'success': True,
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'success': False}), 500



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
    Generate and retrieve a 2-week fitness plan from the database.
    The fitness plan should already be generated and stored in DynamoDB.

    Request body: {} (empty, uses authenticated user's health profile)
    """
    # Import here to avoid circular dependency
    from app.fitness_plan_module.service import FitnessPlanService
    from app.profile_module.service import HealthDataService
    from app.fitness.plan_transformer import mapDatabasePlanToCalendar, PlanParseError
    
    try:
        user_id = get_authenticated_user_id()
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        # Check if user has health profile
        health_svc = HealthDataService()
        health_profile = health_svc.get_health_profile(user_id)
        if not health_profile:
            return jsonify({
                'error': 'No health profile found. Complete health onboarding first.',
                'requiresOnboarding': True
            }), 400
        
        health_dict = health_profile.to_dict()
        if not health_dict.get('fitness_goal'):
            return jsonify({
                'error': 'Fitness goal not set. Complete health onboarding first.',
                'requiresOnboarding': True
            }), 400
        
        # Read fitness plan from DynamoDB
        fp_svc = FitnessPlanService()
        plan_objects = fp_svc.get_by_user(user_id)
        
        if not plan_objects:
            return jsonify({
                'error': 'No fitness plan found for user. Generate a plan first.',
                'success': False
            }), 404
        
        # Convert FitnessPlan objects to dictionaries
        plan_entries = [plan.to_dict() for plan in plan_objects]
        
        # Transform to calendar format
        structured_plan = mapDatabasePlanToCalendar(plan_entries)
        
        return jsonify({
            'success': True,
            'structuredPlan': structured_plan,
            'message': f'Retrieved fitness plan with {len(plan_entries)} exercises.'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e), 'success': False}), 401
    except PlanParseError as e:
        return jsonify({
            'error': 'Failed to format fitness plan',
            'details': str(e),
            'success': False
        }), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'An unexpected error occurred',
            'details': str(e),
            'success': False
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
