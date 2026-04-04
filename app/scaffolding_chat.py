"""
AI recommendation scaffolding for tests and tooling.

This module holds the logic previously exposed as ``POST /api/scaffolding/chat``
on the Flask app. The production app does not register that route.
"""
from __future__ import annotations

import os

from flask import jsonify, request

from app.chatbot.ai_recommendations import get_ai_recommendation
from app.database.models import UserProfile
from app.logger import get_logger

logger = get_logger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def scaffold_chat_post():
    """
    Handle a JSON body with ``message`` and optional ``profile`` (dict).

    Returns a Flask Response (with ``status_code`` set) for direct calls from tests.
    """
    try:
        data = request.get_json() or {}
        message = data.get("message")
        profile_data = data.get("profile", {})

        if not message:
            logger.warning("scaffold_chat: request received without message")
            r = jsonify({"error": "Message is required"})
            r.status_code = 400
            return r

        logger.debug("Creating user profile from request data: %s", profile_data)
        profile = UserProfile.from_dict(profile_data)
        logger.info("User profile created: %s", profile)

        logger.debug("Requesting AI recommendation for user: %s", profile.name)
        response_text = get_ai_recommendation(
            profile=profile,
            message=message,
            api_key=GEMINI_API_KEY,
        )
        logger.info("AI recommendation generated successfully for user: %s", profile.name)

        r = jsonify({"response": response_text})
        r.status_code = 200
        return r

    except ValueError as exc:
        error_msg = str(exc)
        if "GEMINI_API_KEY" in error_msg:
            logger.error("AI service not configured: GEMINI_API_KEY missing")
            r = jsonify(
                {
                    "error": "AI service is not configured. Please set GEMINI_API_KEY in your environment variables."
                }
            )
            r.status_code = 500
            return r
        logger.error("ValueError in scaffold chat: %s", error_msg)
        r = jsonify({"error": error_msg})
        r.status_code = 500
        return r
    except Exception as exc:
        logger.error("Unexpected error in scaffold chat: %s", exc, exc_info=True)
        r = jsonify({"error": f"An error occurred: {exc}"})
        r.status_code = 500
        return r
