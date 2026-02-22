"""
API routes for Fitness Plan (DynamoDB fitness_plan table).
"""
from flask import Blueprint, jsonify, request, session

from app.chat_module.gemini_client import GeminiClient
from app.fitness_plan_module.models import FitnessPlan
from app.fitness_plan_module.service import FitnessPlanService
from app.profile_module.service import HealthDataService

fitness_plan_bp = Blueprint(
    "fitness_plan", __name__, url_prefix="/api/fitness-plan"
)


def _user_id():
    uid = session.get("user_id")
    if not uid:
        raise ValueError("Not authenticated")
    return uid


@fitness_plan_bp.route("", methods=["GET"])
def list_plans():
    """List fitness plan entries for the current user."""
    try:
        user_id = _user_id()
        limit = request.args.get("limit", 100, type=int)
        workout_id_after = request.args.get("workout_id_after")
        svc = FitnessPlanService()
        items = svc.get_by_user(user_id, limit=limit, workout_id_after=workout_id_after)
        return jsonify(
            {
                "fitness_plans": [p.to_dict() for p in items],
                "count": len(items),
            }
        ), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@fitness_plan_bp.route("", methods=["POST"])
def create_plan():
    """Create a fitness plan entry. Body: workout_id, date_of_workout, exercise_name, ..."""
    try:
        user_id = _user_id()
        data = request.get_json() or {}
        workout_id = data.get("workout_id")
        if not workout_id:
            return jsonify({"error": "workout_id is required"}), 400
        plan = FitnessPlan(
            user_id=user_id,
            workout_id=str(workout_id),
            date_of_workout=data.get("date_of_workout"),
            exercise_name=data.get("exercise_name"),
            exercise_description=data.get("exercise_description"),
            rep_count=data.get("rep_count"),
            muscle_group=data.get("muscle_group"),
            expected_calories_burnt=data.get("expected_calories_burnt"),
            weight_to_lift_suggestion=data.get("weight_to_lift_suggestion"),
        )
        FitnessPlanService().create(plan)
        return jsonify({"message": "Created", "fitness_plan": plan.to_dict()}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@fitness_plan_bp.route("/<workout_id>", methods=["GET"])
def get_plan(workout_id: str):
    """Get one fitness plan entry by workout_id."""
    try:
        user_id = _user_id()
        svc = FitnessPlanService()
        plan = svc.get(user_id, workout_id)
        if not plan:
            return jsonify({"error": "Not found", "fitness_plan": None}), 404
        return jsonify({"fitness_plan": plan.to_dict()}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@fitness_plan_bp.route("/<workout_id>", methods=["PUT"])
def update_plan(workout_id: str):
    """Update a fitness plan entry (partial)."""
    try:
        user_id = _user_id()
        data = request.get_json() or {}
        if not data:
            return jsonify({"error": "No body"}), 400
        allowed = {
            "date_of_workout",
            "exercise_name",
            "exercise_description",
            "rep_count",
            "muscle_group",
            "expected_calories_burnt",
            "weight_to_lift_suggestion",
        }
        updates = {k: v for k, v in data.items() if k in allowed and v is not None}
        plan = FitnessPlanService().update(user_id, workout_id, updates)
        return jsonify({"message": "Updated", "fitness_plan": plan.to_dict()}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@fitness_plan_bp.route("/<workout_id>", methods=["DELETE"])
def delete_plan(workout_id: str):
    """Delete a fitness plan entry."""
    try:
        user_id = _user_id()
        FitnessPlanService().delete(user_id, workout_id)
        return jsonify({"message": "Deleted"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _plan_entry_to_bullet(user_id: str, workout_id: str, p: dict) -> str:
    """Format one plan entry as bullet points (all schema fields)."""
    lines = [
        f"• **User ID:** {user_id}",
        f"• **Workout ID:** {workout_id}",
        f"• **Date of workout:** {p.get('date_of_workout') or '—'}",
        f"• **Exercise Name:** {p.get('exercise_name') or '—'}",
        f"• **Exercise Description:** {p.get('exercise_description') or '—'}",
        f"• **Rep Count:** {p.get('rep_count') if p.get('rep_count') is not None else '—'}",
        f"• **Muscle Group:** {p.get('muscle_group') or '—'}",
        f"• **Expected Calories Burnt:** {p.get('expected_calories_burnt') if p.get('expected_calories_burnt') is not None else '—'}",
        f"• **Weight to be lifted (suggestion):** {p.get('weight_to_lift_suggestion') if p.get('weight_to_lift_suggestion') is not None else '—'}",
    ]
    return "\n".join(lines)


@fitness_plan_bp.route("/generate", methods=["POST"])
def generate_plan():
    """
    Parse user health data from DynamoDB and generate a 2-week fitness plan.
    Saves plan to fitness_plan table and returns bullet-point output for each entry.
    """
    try:
        user_id = _user_id()
        health_svc = HealthDataService()
        health_profile = health_svc.get_health_profile(user_id)
        if not health_profile:
            return jsonify({
                "error": "No health profile found. Complete health onboarding first (age, height, weight, gender, fitness goal).",
            }), 400
        health_dict = health_profile.to_dict()
        if not health_dict.get("fitness_goal"):
            return jsonify({
                "error": "Fitness goal not set. Complete health onboarding first.",
            }), 400
        gemini = GeminiClient()
        plan_entries = gemini.generate_two_week_fitness_plan(health_dict)
        if not plan_entries:
            return jsonify({"error": "Could not generate plan", "bullet_points": [], "fitness_plans": []}), 422
        fp_svc = FitnessPlanService()
        saved = []
        bullets = []
        for i, entry in enumerate(plan_entries):
            date_val = entry.get("date_of_workout") or ""
            workout_id = f"{date_val}-{i}"
            plan = FitnessPlan(
                user_id=user_id,
                workout_id=workout_id,
                date_of_workout=entry.get("date_of_workout"),
                exercise_name=entry.get("exercise_name"),
                exercise_description=entry.get("exercise_description"),
                rep_count=entry.get("rep_count"),
                muscle_group=entry.get("muscle_group"),
                expected_calories_burnt=entry.get("expected_calories_burnt"),
                weight_to_lift_suggestion=entry.get("weight_to_lift_suggestion"),
            )
            fp_svc.create(plan)
            d = plan.to_dict()
            saved.append(d)
            bullets.append(_plan_entry_to_bullet(user_id, workout_id, d))
        return jsonify({
            "message": f"Generated and saved {len(saved)} exercises for your 2-week plan.",
            "bullet_points": bullets,
            "fitness_plans": saved,
            "count": len(saved),
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
