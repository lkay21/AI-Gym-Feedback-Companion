from __future__ import annotations

from datetime import datetime, timezone
import uuid

from app.db_instance import db


class WorkoutSnapshot(db.Model):
    __tablename__ = "workout_snapshot"

    snapshot_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    workout_id = db.Column(db.String(64), nullable=False)
    workout_type = db.Column(db.String(120), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    total_volume = db.Column(db.Float, nullable=False)
    calories_burned = db.Column(db.Integer, nullable=False)
    average_heart_rate = db.Column(db.Integer)
    exercises_completed = db.Column(db.JSON, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self) -> dict:
        def _iso(dt: datetime | None) -> str | None:
            if not dt:
                return None
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.isoformat()

        return {
            "snapshot_id": self.snapshot_id,
            "user_id": self.user_id,
            "workout_id": self.workout_id,
            "workout_type": self.workout_type,
            "duration_minutes": self.duration_minutes,
            "total_volume": self.total_volume,
            "calories_burned": self.calories_burned,
            "average_heart_rate": self.average_heart_rate,
            "exercises_completed": self.exercises_completed,
            "completed_at": _iso(self.completed_at),
            "created_at": _iso(self.created_at),
        }
