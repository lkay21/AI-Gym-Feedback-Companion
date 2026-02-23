from __future__ import annotations

from typing import List, Optional

from app.db_instance import db
from app.workout_snapshot.models import WorkoutSnapshot


class WorkoutSnapshotService:
    def create(self, snapshot: WorkoutSnapshot) -> WorkoutSnapshot:
        db.session.add(snapshot)
        db.session.commit()
        return snapshot

    def get(self, snapshot_id: str) -> Optional[WorkoutSnapshot]:
        return db.session.get(WorkoutSnapshot, snapshot_id)

    def list_by_user(self, user_id: int, limit: int = 20, offset: int = 0) -> List[WorkoutSnapshot]:
        return (
            WorkoutSnapshot.query
            .filter_by(user_id=user_id)
            .order_by(WorkoutSnapshot.completed_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def count_by_user(self, user_id: int) -> int:
        return WorkoutSnapshot.query.filter_by(user_id=user_id).count()
