"""Deprecated: use app.chatbot.routes instead."""
from app.chatbot.routes import chat_bp, chat, health_check, validate_chat_request, get_authenticated_user_id

__all__ = [
    "chat_bp",
    "chat",
    "health_check",
    "validate_chat_request",
    "get_authenticated_user_id",
]

