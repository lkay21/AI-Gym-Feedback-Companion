from datetime import datetime

from app.db_instance import db


class VideoAsset(db.Model):
    __tablename__ = 'video_assets'

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
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
