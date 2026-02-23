from __future__ import annotations

from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError

from app.db_instance import db
from app.core.errors import DatabaseError
from app.workout_snapshot.models import WorkoutSnapshot


class WorkoutSnapshotService:
    def create(self, snapshot: WorkoutSnapshot) -> WorkoutSnapshot:
        try:
            db.session.add(snapshot)
            db.session.commit()
            return snapshot
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DatabaseError("Failed to create workout snapshot") from exc

    def get(self, snapshot_id: str) -> Optional[WorkoutSnapshot]:
        try:
            return db.session.get(WorkoutSnapshot, snapshot_id)
        except SQLAlchemyError as exc:
            raise DatabaseError("Failed to fetch workout snapshot") from exc

    def list_by_user(self, user_id: int, limit: int = 20, offset: int = 0) -> List[WorkoutSnapshot]:
        try:
            return (
                WorkoutSnapshot.query
                .filter_by(user_id=user_id)
                .order_by(WorkoutSnapshot.completed_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as exc:
            raise DatabaseError("Failed to list workout snapshots") from exc

    def count_by_user(self, user_id: int) -> int:
        try:
            return WorkoutSnapshot.query.filter_by(user_id=user_id).count()
        except SQLAlchemyError as exc:
            raise DatabaseError("Failed to count workout snapshots") from exc

    def exists_duplicate(self, user_id: int, workout_id: str, completed_at) -> bool:
        try:
            return (
                WorkoutSnapshot.query
                .filter_by(user_id=user_id, workout_id=workout_id, completed_at=completed_at)
                .first()
                is not None
            )
        except SQLAlchemyError as exc:
            raise DatabaseError("Failed to validate workout snapshot uniqueness") from exc
