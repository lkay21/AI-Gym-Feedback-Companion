"""
API routes for Fitness Plan (DynamoDB fitness_plan table).
"""
from flask import Blueprint, jsonify, request, session

from app.fitness_plan_module.models import FitnessPlan
from app.fitness_plan_module.service import FitnessPlanService

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

