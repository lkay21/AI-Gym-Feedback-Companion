"""
Generate and persist 2-week fitness plans (DynamoDB). Used by chat flows.

Plan generation logic (no separate REST blueprint).
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from flask import jsonify

from app.chat_module.gemini_client import GeminiClient
from app.fitness.plan_models import FitnessPlan
from app.fitness.plan_service import FitnessPlanService
from app.profile_module.service import HealthDataService


def _plan_entry_to_bullet(user_id: str, workout_id: str, p: dict) -> str:
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


def generate_two_week_plan_and_save(user_id: str) -> Tuple[Any, int]:
    """
    Load health profile, call Gemini, save rows to fitness_plan.

    Returns a Flask (response, status_code) tuple for optional HTTP use.
    """
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    health_svc = HealthDataService()
    health_profile = health_svc.get_health_profile(user_id)
    if not health_profile:
        return jsonify(
            {
                "error": "No health profile found. Complete health onboarding first (age, height, weight, gender, fitness goal).",
            }
        ), 400

    health_dict = health_profile.to_dict()
    if not health_dict.get("fitness_goal"):
        return jsonify(
            {
                "error": "Fitness goal not set. Complete health onboarding first.",
            }
        ), 400

    gemini = GeminiClient()
    plan_entries = gemini.generate_two_week_fitness_plan(health_dict)
    if not plan_entries:
        return jsonify({"error": "Could not generate plan", "bullet_points": [], "fitness_plans": []}), 422

    fp_svc = FitnessPlanService()
    saved: List[Dict[str, Any]] = []
    bullets: List[str] = []
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

    return jsonify(
        {
            "message": f"Generated and saved {len(saved)} exercises for your 2-week plan.",
            "bullet_points": bullets,
            "fitness_plans": saved,
            "count": len(saved),
        }
    ), 200
