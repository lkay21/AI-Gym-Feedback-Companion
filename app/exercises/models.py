from datetime import datetime
import uuid

from app.db_instance import db


class VideoAsset(db.Model):
    __tablename__ = 'video_assets'

    # UUID primary key prevents predictable identifier enumeration.
    asset_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_user_id = db.Column(db.String(128), nullable=False, index=True)
    exercise = db.Column(db.String(128), nullable=False)
    original_filename = db.Column(db.String(256), nullable=False)
    raw_s3_key = db.Column(db.String(512), nullable=False)
    pose_s3_key = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'asset_id': self.asset_id,
            'owner_user_id': self.owner_user_id,
            'exercise': self.exercise,
            'original_filename': self.original_filename,
            'raw_s3_key': self.raw_s3_key,
            'pose_s3_key': self.pose_s3_key,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }