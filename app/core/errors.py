from __future__ import annotations

from typing import Any, Dict, Optional


class AppError(Exception):
    status_code = 500

    def __init__(self, message: str, metadata: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.metadata = metadata or {}


class ValidationError(AppError):
    status_code = 400


class NotFoundError(AppError):
    status_code = 404


class DatabaseError(AppError):
    status_code = 500


class UnauthorizedError(AppError):
    status_code = 401
