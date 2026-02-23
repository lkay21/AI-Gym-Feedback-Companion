from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from flask import Blueprint, jsonify, request, current_app

from app.auth_module.models import User
from app.db_instance import db
from app.core.errors import NotFoundError, ValidationError
from app.workout_snapshot.models import WorkoutSnapshot
from app.workout_snapshot.service import WorkoutSnapshotService


workout_snapshot_bp = Blueprint("workout_snapshot", __name__, url_prefix="/api")


REQUIRED_FIELDS = {
    "user_id",
    "workout_id",
    "workout_type",
    "duration_minutes",
    "total_volume",
    "calories_burned",
    "exercises_completed",
    "completed_at",
}


def _parse_iso_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def _validate_positive_int(name: str, value: Any) -> None:
    if not isinstance(value, int) or value <= 0:
        raise ValidationError(f"{name} must be a positive integer")


def _validate_positive_number(name: str, value: Any) -> None:
    if not isinstance(value, (int, float)) or value <= 0:
        raise ValidationError(f"{name} must be a positive number")


def _validate_exercises_completed(value: Any) -> None:
    if not isinstance(value, list):
        raise ValidationError("exercises_completed must be an array of objects")
    if any(not isinstance(item, dict) for item in value):
        raise ValidationError("exercises_completed must contain only objects")


def _get_user(user_id: Any) -> Optional[User]:
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        return None
    return db.session.get(User, user_id_int)


def _parse_request_data() -> dict:
    if request.content_length is not None:
        max_len = current_app.config.get("MAX_CONTENT_LENGTH")
        if max_len is not None and request.content_length > max_len:
            raise ValidationError("Payload too large")
    data = request.get_json(silent=True)
    if data is None:
        raise ValidationError("Malformed JSON payload")
    return data


@workout_snapshot_bp.route("/workout-snapshots", methods=["POST"])
def create_workout_snapshot():
    data = _parse_request_data()

    missing = [key for key in REQUIRED_FIELDS if key not in data]
    if missing:
        raise ValidationError(f"Missing required fields: {', '.join(sorted(missing))}")

    user = _get_user(data.get("user_id"))
    if not user:
        raise NotFoundError("User not found")

    _validate_positive_int("duration_minutes", data.get("duration_minutes"))
    _validate_positive_number("total_volume", data.get("total_volume"))
    _validate_positive_int("calories_burned", data.get("calories_burned"))

    if data.get("average_heart_rate") is not None:
        _validate_positive_int("average_heart_rate", data.get("average_heart_rate"))

    _validate_exercises_completed(data.get("exercises_completed"))

    completed_at = _parse_iso_datetime(data.get("completed_at"))
    if not completed_at:
        raise ValidationError("completed_at must be an ISO timestamp")

    svc = WorkoutSnapshotService()
    if svc.exists_duplicate(int(user.id), str(data.get("workout_id")), completed_at):
        raise ValidationError("Workout snapshot already exists")

    snapshot = WorkoutSnapshot(
        user_id=int(user.id),
        workout_id=str(data.get("workout_id")),
        workout_type=str(data.get("workout_type")),
        duration_minutes=int(data.get("duration_minutes")),
        total_volume=float(data.get("total_volume")),
        calories_burned=int(data.get("calories_burned")),
        average_heart_rate=(
            int(data.get("average_heart_rate"))
            if data.get("average_heart_rate") is not None
            else None
        ),
        exercises_completed=data.get("exercises_completed"),
        completed_at=completed_at,
    )

    snapshot = svc.create(snapshot)
    return jsonify({"snapshot": snapshot.to_dict()}), 201


@workout_snapshot_bp.route("/workout-snapshots/<snapshot_id>", methods=["GET"])
def get_workout_snapshot(snapshot_id: str):
    snapshot = WorkoutSnapshotService().get(snapshot_id)
    if not snapshot:
        raise NotFoundError("Workout snapshot not found")
    return jsonify({"snapshot": snapshot.to_dict()}), 200


@workout_snapshot_bp.route("/users/<user_id>/workout-snapshots", methods=["GET"])
def list_workout_snapshots(user_id: str):
    user = _get_user(user_id)
    if not user:
        raise NotFoundError("User not found")

    limit = request.args.get("limit", 20, type=int)
    offset = request.args.get("offset", 0, type=int)
    if limit <= 0:
        raise ValidationError("limit must be a positive integer")
    if offset < 0:
        raise ValidationError("offset must be zero or a positive integer")

    svc = WorkoutSnapshotService()
    snapshots = svc.list_by_user(user.id, limit=limit, offset=offset)
    total = svc.count_by_user(user.id)

    return jsonify({
        "snapshots": [snapshot.to_dict() for snapshot in snapshots],
        "count": len(snapshots),
        "total": total,
        "limit": limit,
        "offset": offset,
    }), 200
