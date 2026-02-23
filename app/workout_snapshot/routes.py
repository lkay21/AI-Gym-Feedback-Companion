from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from flask import Blueprint, jsonify, request

from app.auth_module.models import User
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
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _validate_positive_int(name: str, value: Any) -> Optional[str]:
    if not isinstance(value, int) or value <= 0:
        return f"{name} must be a positive integer"
    return None


def _validate_positive_number(name: str, value: Any) -> Optional[str]:
    if not isinstance(value, (int, float)) or value <= 0:
        return f"{name} must be a positive number"
    return None


def _validate_exercises_completed(value: Any) -> Optional[str]:
    if not isinstance(value, list):
        return "exercises_completed must be an array of objects"
    if any(not isinstance(item, dict) for item in value):
        return "exercises_completed must contain only objects"
    return None


def _get_user(user_id: Any) -> Optional[User]:
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        return None
    return User.query.get(user_id_int)


@workout_snapshot_bp.route("/workout-snapshots", methods=["POST"])
def create_workout_snapshot():
    data = request.get_json(silent=True) or {}

    missing = [key for key in REQUIRED_FIELDS if key not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(sorted(missing))}"}), 400

    user = _get_user(data.get("user_id"))
    if not user:
        return jsonify({"error": "User not found"}), 404

    error = _validate_positive_int("duration_minutes", data.get("duration_minutes"))
    if error:
        return jsonify({"error": error}), 400

    error = _validate_positive_number("total_volume", data.get("total_volume"))
    if error:
        return jsonify({"error": error}), 400

    error = _validate_positive_int("calories_burned", data.get("calories_burned"))
    if error:
        return jsonify({"error": error}), 400

    if data.get("average_heart_rate") is not None:
        error = _validate_positive_int("average_heart_rate", data.get("average_heart_rate"))
        if error:
            return jsonify({"error": error}), 400

    error = _validate_exercises_completed(data.get("exercises_completed"))
    if error:
        return jsonify({"error": error}), 400

    completed_at = _parse_iso_datetime(data.get("completed_at"))
    if not completed_at:
        return jsonify({"error": "completed_at must be an ISO timestamp"}), 400

    snapshot = WorkoutSnapshot(
        user_id=int(data.get("user_id")),
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

    try:
        snapshot = WorkoutSnapshotService().create(snapshot)
        return jsonify({"snapshot": snapshot.to_dict()}), 201
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@workout_snapshot_bp.route("/workout-snapshots/<snapshot_id>", methods=["GET"])
def get_workout_snapshot(snapshot_id: str):
    snapshot = WorkoutSnapshotService().get(snapshot_id)
    if not snapshot:
        return jsonify({"error": "Workout snapshot not found"}), 404
    return jsonify({"snapshot": snapshot.to_dict()}), 200


@workout_snapshot_bp.route("/users/<user_id>/workout-snapshots", methods=["GET"])
def list_workout_snapshots(user_id: str):
    user = _get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    limit = request.args.get("limit", 20, type=int)
    offset = request.args.get("offset", 0, type=int)
    if limit <= 0:
        return jsonify({"error": "limit must be a positive integer"}), 400
    if offset < 0:
        return jsonify({"error": "offset must be zero or a positive integer"}), 400

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
