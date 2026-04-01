#!/usr/bin/env python3
"""
Test the 2-week fitness plan generation: load health data from DynamoDB, call Gemini,
save to fitness_plan table, output bullet points.

Usage:
  # Use a test user with a health profile already in DynamoDB (run health onboarding first)
  python scripts/test_fitness_plan_generate.py

  # Or use your real user (must have completed health onboarding in the app)
  USER_ID=your-real-user-id python scripts/test_fitness_plan_generate.py

  # Seed a minimal health profile for the test user (no onboarding needed)
  SEED_HEALTH=1 python scripts/test_fitness_plan_generate.py
"""
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    from app.main import create_app
    from app.profile_module.service import HealthDataService
    from app.profile_module.models import HealthData, HEALTH_PROFILE_TIMESTAMP

    app = create_app()
    user_id = os.environ.get("USER_ID", "test-user-plan")
    seed_health = os.environ.get("SEED_HEALTH", "").strip().lower() in ("1", "true", "yes")

    with app.app_context():
        if seed_health:
            # Create/update health profile so generate has something to read
            health_svc = HealthDataService()
            health_svc.create_or_update_health_profile(
                user_id,
                age=28,
                height=175,
                weight=70,
                gender="male",
                fitness_goal="build muscle",
                context={"pending_fixed": [], "qa_pairs": [], "pending_questions": []},
            )
            print(f"Seeded health profile for user_id={user_id}\n")

    from app.fitness.plan_generation import generate_two_week_plan_and_save

    with app.app_context():
        resp, status = generate_two_week_plan_and_save(user_id)
        data = resp.get_json() if resp.content_type and "json" in resp.content_type else None

        if status != 200:
            print("Generate failed:", status)
            print(data or resp.get_data(as_text=True))
            return 1

        print("--- 2-week fitness plan (bullet points) ---\n")
        bullets = data.get("bullet_points") or []
        for i, b in enumerate(bullets):
            print(b)
            if i < len(bullets) - 1:
                print()
        print("\n--- Summary ---")
        print(f"Saved {data.get('count', 0)} exercises to fitness_plan table.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
