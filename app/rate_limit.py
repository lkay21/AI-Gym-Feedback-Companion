import os

from flask import jsonify, request
from flask_limiter import Limiter
from flask_limiter.errors import RateLimitExceeded
from flask_limiter.util import get_remote_address

from app.auth_module.utils import resolve_authenticated_user_id
from app.logger import get_logger


logger = get_logger(__name__)

_storage_uri = os.getenv("RATELIMIT_STORAGE_URI", "memory://")

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    storage_uri=_storage_uri,
    headers_enabled=True,
)


def _rate_limit_exceeded_handler(error: RateLimitExceeded):
    user_id = resolve_authenticated_user_id() or "anonymous"
    ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
    logger.warning(
        "Rate limit exceeded path=%s method=%s user_id=%s ip=%s limit=%s",
        request.path,
        request.method,
        user_id,
        ip_address,
        str(error.description),
    )
    return jsonify({
        "error": "Rate limit exceeded",
        "detail": str(error.description),
    }), 429


def init_rate_limiter(app):
    limiter.init_app(app)
    app.register_error_handler(429, _rate_limit_exceeded_handler)
