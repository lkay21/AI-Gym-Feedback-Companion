"""
API routes for chatbot functionality
"""
from flask import Blueprint, request, jsonify, session
from typing import Dict, Any, Optional, Tuple
from datetime import date

from app.chatbot.llm_service import generate_llm_response, validateFitnessPlanSchema
from app.chatbot.gemini_client import GeminiClient
from app.fitness.plan_transformer import mapLLMPlanToStructuredPlan, mapDatabasePlanToCalendar
from app.fitness_plan_module.service import FitnessPlanService
from app.profile_module.service import HealthDataService

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")


def get_authenticated_user_id() -> Optional[str]:
    """Get authenticated user ID from session."""
    return session.get("user_id")


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


@chat_bp.route("", methods=["POST"])
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
        # Validate request
        data = request.get_json()
        is_valid, error_msg = validate_chat_request(data)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
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

        return jsonify(result), 500
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'An unexpected error occurred',
            'details': str(e)
        }), 500


@chat_bp.route("/llm", methods=["POST"])
def chat_gemini():
    """
    Conversational LLM endpoint used by the mobile ChatBot screen.

    Behaviour:
    - If the user has a saved fitness plan in DynamoDB, the AI gets a summarized view
      of that plan and should answer general questions about it instead of generating
      a brand new plan.
    - If no plan exists yet, the endpoint reuses the existing health-onboarding flow
      (fixed stats → fitness goal → 2–3 follow-ups) to populate HealthData, then calls
      the existing fitness plan generator to create and store a 2-week plan, and only
      after that switches into plan-aware Q&A mode.
    - When available, the user's health profile from DynamoDB is passed as context
      (age, height, weight, gender, fitness_goal).
    """
    try:
        user_id = get_authenticated_user_id()
        data = request.get_json() or {}

        message = (data.get("message") or "").strip()
        if not message:
            return jsonify({"error": "Message is required and cannot be empty"}), 400

        conversation_history = data.get("conversation_history") or []
        user_profile = data.get("profile") or {}

        has_plan = False
        plans = []

        # If authenticated, check for an existing fitness plan.
        if user_id:
            fp_svc = FitnessPlanService()
            try:
                plans = fp_svc.get_by_user(user_id, limit=50)
                has_plan = bool(plans)
            except Exception as exc:  # pragma: no cover - defensive
                print(f"Warning: failed to load fitness plan for {user_id}: {exc}")

            # If no plan yet, drive the existing health-onboarding flow and then generate a plan.
            if not has_plan:
                # Reuse health_onboarding from app.chat_module.routes
                from app.chat_module.routes import health_onboarding as onboarding_route
                from app.fitness_plan_module.routes import generate_plan as generate_plan_route

                onboarding_resp = onboarding_route()
                try:
                    onboarding_json = onboarding_resp.get_json() or {}
                except Exception:
                    onboarding_json = {}

                phase = onboarding_json.get("phase")

                # While onboarding is in progress (not complete), just surface its response.
                if phase != "complete":
                    onboarding_json.setdefault("has_plan", False)
                    return jsonify(onboarding_json), onboarding_resp.status_code

                # Onboarding completed: invoke the existing fitness-plan generation logic.
                try:
                    generate_plan_route()
                except Exception as exc:  # pragma: no cover - defensive
                    print(f"Warning: failed to generate fitness plan for {user_id}: {exc}")

                # Reload plans after generation attempt.
                try:
                    plans = fp_svc.get_by_user(user_id, limit=50)
                    has_plan = bool(plans)
                except Exception as exc:  # pragma: no cover - defensive
                    print(f"Warning: failed to reload fitness plan for {user_id}: {exc}")

        # Enrich profile with health data from DynamoDB, if available.
        if user_id:
            try:
                health_svc = HealthDataService()
                health_profile = health_svc.get_health_profile(user_id)
                if health_profile:
                    hp_dict = {
                        "age": getattr(health_profile, "age", None),
                        "height": getattr(health_profile, "height", None),
                        "weight": getattr(health_profile, "weight", None),
                        "gender": getattr(health_profile, "gender", None),
                    }
                    fg = getattr(health_profile, "fitness_goal", None)
                    if fg:
                        hp_dict["fitness_goals"] = [fg]

                    for k, v in hp_dict.items():
                        if v is not None and k not in user_profile:
                            user_profile[k] = v
            except Exception as exc:  # pragma: no cover - defensive
                print(f"Warning: failed to load health profile for {user_id}: {exc}")

            # If we now have a plan, attach a short summary for plan-aware Q&A.
            if has_plan and plans:
                try:
                    plan_entries = [p.to_dict() for p in plans]
                    calendar = mapDatabasePlanToCalendar(plan_entries)
                    user_profile.setdefault(
                        "fitness_plan_summary", _summarize_calendar_plan(calendar)
                    )
                except Exception as exc:  # pragma: no cover - defensive
                    print(f"Warning: failed to summarize fitness plan for {user_id}: {exc}")

        # Call Gemini with conversation + enriched profile context.
        gemini = GeminiClient()
        response_text = gemini.generate_response(
            user_message=message,
            conversation_history=conversation_history,
            user_profile=user_profile or None,
        )

        return (
            jsonify(
                {
                    "success": True,
                    "response": response_text,
                    "has_plan": has_plan,
                }
            ),
            200,
        )
    except Exception as e:  # pragma: no cover - defensive
        import traceback

        traceback.print_exc()
        return (
            jsonify(
                {
                    "error": "Failed to generate chatbot response",
                    "details": str(e),
                    "success": False,
                }
            ),
            500,
        )


@chat_bp.route('/init', methods=['POST'])
def init_plan():
    """Initialize and retrieve the 2-week fitness plan from DynamoDB"""
    try:
        user_id = get_authenticated_user_id()
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401

        # Retrieve the 2-week fitness plan from DynamoDB
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
            'data': structured_plan
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'An error occurred: {str(e)}', 'success': False}), 500


def _summarize_calendar_plan(calendar_plan: Dict[str, Any]) -> str:
    """
    Build a short, human-readable summary of the existing fitness plan for the LLM.

    We only need a concise overview so the assistant can answer questions about
    the plan without regenerating it from scratch.
    """
    if not isinstance(calendar_plan, dict):
        return ""

    weeks = calendar_plan.get("weeks") or []
    if not weeks:
        return ""

    lines: list[str] = []
    for week in weeks:
        week_num = week.get("weekNumber")
        days = week.get("days") or []
        for day in days:
            date_str = day.get("date")
            workout_type = day.get("workoutType") or "Workout"
            exercises = day.get("exercises") or []
            if not exercises and workout_type.lower() == "rest":
                lines.append(f"{date_str}: Rest day")
                continue

            # Summarize exercise names for that day
            names = [
                (ex.get("name") or "").strip()
                for ex in exercises
                if (ex.get("name") or "").strip()
            ]
            if names:
                ex_summary = ", ".join(names[:4])
                if len(names) > 4:
                    ex_summary += ", ..."
                lines.append(
                    f"{date_str} (Week {week_num}): {workout_type} - {ex_summary}"
                )
            else:
                lines.append(f"{date_str} (Week {week_num}): {workout_type}")

    # Keep it short – the assistant doesn't need every single detail
    return "\n".join(lines[:20])


@chat_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for chat service"""
    try:
        # Verify OpenAI configuration
        from os import getenv
        api_key = getenv("OPENAI_API_KEY")
        model_name = getenv("MODEL_NAME", "gpt-4o-mini")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set in environment variables")
        return jsonify({
            'status': 'healthy',
            'service': 'chat',
            'model': model_name,
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


@chat_bp.route('/health/llm', methods=['GET'])
def llm_health_check():
    """Health check endpoint for LLM service"""
    try:
        from os import getenv
        api_key = getenv("OPENAI_API_KEY")
        model_name = getenv("MODEL_NAME", "gpt-4o-mini")
        if not api_key:
            return jsonify({
                'status': 'unhealthy',
                'service': 'llm',
                'configured': False,
                'error': 'OPENAI_API_KEY is not set'
            }), 503
        return jsonify({
            'status': 'healthy',
            'service': 'llm',
            'configured': True,
            'model': model_name
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'service': 'llm',
            'error': str(e)
        }), 500