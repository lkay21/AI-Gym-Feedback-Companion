"""
Backfill script to sync all Supabase users into the DynamoDB user_profiles table.

Usage (from project root, with venv + env vars configured):

    python -m scripts.backfill_user_profiles_from_supabase
"""

from app.auth_module.supabase_client import get_supabase_client
from app.profile_module.service import ProfileService
from app.profile_module.models import UserProfile


def backfill_user_profiles(page_size: int = 100) -> None:
    """
    Iterate through all Supabase users and ensure there is a corresponding
    DynamoDB user_profiles row (keyed by Supabase user.id).
    """
    supabase = get_supabase_client()
    profile_service = ProfileService()

    page = 1
    created = 0
    skipped = 0

    while True:
        # supabase-py admin list_users API; adjust if SDK surface changes
        resp = supabase.auth.admin.list_users(page=page, per_page=page_size)
        users = getattr(resp, "users", []) or []
        if not users:
            break

        for user in users:
            uid = getattr(user, "id", None)
            if not uid:
                continue

            existing = profile_service.get_profile(uid)
            if existing:
                skipped += 1
                continue

            profile_service.create_profile(UserProfile(user_id=uid))
            created += 1
            print(f"Created profile for Supabase user {uid}")

        page += 1

    print(f"Backfill complete. Created: {created}, existing skipped: {skipped}")


if __name__ == "__main__":
    backfill_user_profiles()

