#!/usr/bin/env python3
"""
Interactive test of the health-onboarding API. You type your own goal and answers.
Uses Flask test client with a session (no browser login). Set USER_ID in env to use your real user.
"""
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    from app.main import create_app

    app = create_app()
    user_id = os.environ.get("USER_ID", "test-user-interactive2")

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = user_id
            sess["username"] = "testuser"

        def post(message: str):
            r = client.post(
                "/api/chat/health-onboarding",
                json={"message": message},
                content_type="application/json",
            )
            if r.status_code != 200:
                print("API error:", r.status_code, r.get_data(as_text=True))
                return None
            return r.get_json()

        print("--- Health onboarding API (your inputs) ---")
        print("User ID for this run:", user_id)
        print()

        data = post("")
        if not data or not data.get("success"):
            print("Failed to get intro:", data)
            return 1
        print("AI:", data["response"])
        print()

        # 1) Fixed characteristics (age, height, weight, gender) if in ask_fixed
        while data.get("phase") == "ask_fixed":
            ans = input("Your answer: ").strip()
            if not ans:
                ans = "28" if "age" in data.get("response", "").lower() else "175" if "height" in data.get("response", "").lower() else "70" if "weight" in data.get("response", "").lower() else "male"
            data = post(ans)
            if not data or not data.get("success"):
                print("Failed:", data)
                return 1
            print("AI:", data["response"])
            print()

        # 2) Fitness goal (if we're at ask_goal)
        if data.get("phase") == "ask_goal":
            goal = input("Your fitness goal? ").strip() or "get fit"
            data = post(goal)
            if not data or not data.get("success"):
                print("Failed:", data)
                return 1
            print("AI:", data["response"])
            print()

        # 3) Follow-ups until complete
        while data.get("phase") == "follow_up":
            ans = input("Your answer: ").strip() or "(skipped)"
            data = post(ans)
            if not data or not data.get("success"):
                print("Failed:", data)
                return 1
            print("AI:", data["response"])
            print()

        print("Done. Phase:", data.get("phase", "?"))


if __name__ == "__main__":
    sys.exit(main() or 0)
