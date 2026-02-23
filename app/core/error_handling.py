from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from flask import Flask, jsonify, request, g, session
from werkzeug.exceptions import BadRequest, RequestEntityTooLarge

from app.core.errors import AppError
from app.logger import get_logger


logger = get_logger(__name__)


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_user_id() -> Optional[str]:
    user_id = session.get("user_id")
    if user_id is not None:
        return str(user_id)
    payload = request.get_json(silent=True) or {}
    if isinstance(payload, dict) and payload.get("user_id") is not None:
        return str(payload.get("user_id"))
    return None


def _log_error(error_type: str, message: str) -> None:
    logger.error(
        {
            "requestId": getattr(g, "request_id", None),
            "route": request.path,
            "method": request.method,
            "userId": _get_user_id(),
            "errorType": error_type,
            "message": message,
            "timestamp": _utc_timestamp(),
        }
    )


def _error_response(error_type: str, message: str):
    return jsonify(
        {
            "success": False,
            "error": {
                "type": error_type,
                "message": message,
                "requestId": getattr(g, "request_id", None),
                "timestamp": _utc_timestamp(),
            },
        }
    )


def register_error_handlers(app: Flask) -> None:
    @app.before_request
    def _assign_request_id() -> None:
        g.request_id = str(uuid4())

    @app.after_request
    def _attach_request_id(response):
        request_id = getattr(g, "request_id", None)
        if request_id:
            response.headers["X-Request-Id"] = request_id
        return response

    @app.errorhandler(AppError)
    def _handle_app_error(error: AppError):
        _log_error(error.__class__.__name__, error.message)
        response = _error_response(error.__class__.__name__, error.message)
        return response, error.status_code

    @app.errorhandler(RequestEntityTooLarge)
    def _handle_payload_too_large(_error: RequestEntityTooLarge):
        message = "Payload too large"
        _log_error("ValidationError", message)
        response = _error_response("ValidationError", message)
        return response, 400

    @app.errorhandler(BadRequest)
    def _handle_bad_request(_error: BadRequest):
        message = "Malformed JSON payload"
        _log_error("ValidationError", message)
        response = _error_response("ValidationError", message)
        return response, 400

    @app.errorhandler(Exception)
    def _handle_unexpected(error: Exception):
        message = "An unexpected error occurred"
        _log_error(error.__class__.__name__, message)
        response = _error_response("DatabaseError", message)
        return response, 500
