# API routes for handling user video uploads, pose generation, and feedback 
# new branch
from flask import Blueprint, request, jsonify
import boto3
from dotenv import load_dotenv
import os
import uuid
from werkzeug.utils import secure_filename
from .openpose import user_output
from app.db_instance import db
from app.auth_module.utils import resolve_authenticated_user_id
from .models import VideoAsset

load_dotenv()

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION = os.getenv('AWS_REGION')

bucket_name = 'fitness-form-videos'

s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION)

exercises_bp = Blueprint('exercises', __name__)
EXERCISES_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_IN_DIR = os.path.join(EXERCISES_DIR, 'video_in')

# Might have to map frontend naming to EXERCISE PRESETS
# IMPORTANT #
# Function assumes input video file is inside video_in folder within exercises directory, for final application this will likely become the following process:
# 1. User uploads video through frontend, video is sent to backend and stored in S3 bucket
# 2. Backend retrieves video from S3 bucket and stores it in video_in folder
# 3. Function processes and both video and pose estimation are in S3 bucket for frontend to retrieve and display
# 4. Delete video from local folder as any further use will occur through S3
def _build_insight_from_context(context_dict):
    focus_areas = []

    for joint, issues in (context_dict or {}).items():
        if not issues:
            continue

        axes = set()
        for issue in issues:
            parts = [part.strip() for part in issue.split(',')]
            if len(parts) >= 2:
                axes.add(parts[1].upper())

        if not axes:
            continue

        axis_text = "/".join(sorted(axes))
        focus_areas.append(f"{joint} ({axis_text})")

    if not focus_areas:
        return "Great job. Your movement pattern is close to the reference form."

    return "Focus on improving alignment at: " + ", ".join(focus_areas) + "."


def parse_user_video(video_file, exercise, user_id):

    # ensure coorect video file type
    # video_file = check_file_type(video_file)

    input_video_path = os.path.join(VIDEO_IN_DIR, video_file)
    video_file_name = user_id + '_' + exercise + '?' + video_file + '_raw'
    # upload raw video to S3
    with open(input_video_path, 'rb') as vfile:
        s3.upload_fileobj(vfile, bucket_name, video_file_name)

    overall_score, joint_scores, context_dict, _, _, llm_feedback = user_output(
        video_file, exercise, user_id, aws_upload=True
    )

    numeric_score = round(float(overall_score) * 100, 2)

    return {
        "form_score": numeric_score,
        "joint_scores": {k: round(float(v) * 100, 2) for k, v in joint_scores.items()},
        "insight": llm_feedback,
        "feedback": llm_feedback,
        "raw_insights": context_dict,
    }


def _build_s3_asset_keys(filename, exercise, owner_user_id):
    raw_key = owner_user_id + '_' + exercise + '?' + filename + '_raw'
    pose_key = owner_user_id + '_' + exercise + '?' + filename
    return raw_key, pose_key


def _create_video_asset(owner_user_id, exercise, filename):
    raw_key, pose_key = _build_s3_asset_keys(filename, exercise, owner_user_id)
    asset = VideoAsset(
        owner_user_id=owner_user_id,
        exercise=exercise,
        original_filename=filename,
        raw_s3_key=raw_key,
        pose_s3_key=pose_key,
    )
    db.session.add(asset)
    db.session.commit()
    return asset


def _get_request_user_id_or_401():
    request_user_id = resolve_authenticated_user_id()
    if not request_user_id:
        return None, (jsonify({'error': 'Authentication required'}), 401)
    return request_user_id, None


def _validate_uuid_or_400(asset_id):
    try:
        uuid.UUID(str(asset_id))
        return None
    except (ValueError, TypeError):
        return jsonify({'error': 'asset_id must be a valid UUID'}), 400


def _get_owned_asset_or_error(asset_id):
    request_user_id, auth_error = _get_request_user_id_or_401()
    if auth_error:
        return None, auth_error

    uuid_error = _validate_uuid_or_400(asset_id)
    if uuid_error:
        return None, uuid_error

    asset = db.session.get(VideoAsset, asset_id)
    if not asset:
        return None, (jsonify({'error': 'Video asset not found'}), 404)

    if str(asset.owner_user_id) != str(request_user_id):
        return None, (jsonify({'error': 'Not authorized to access this video resource'}), 403)

    return asset, None


def _build_presigned_get_url(s3_key, expires_seconds=900):
    return s3.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': bucket_name,
            'Key': s3_key,
        },
        ExpiresIn=expires_seconds,
    )


@exercises_bp.route('/analyze', methods=['POST'])
def analyze_video():
    print(f"[CV] /analyze received files={list(request.files.keys())}, form_keys={list(request.form.keys())}")

    video = request.files.get('video')
    exercise = request.form.get('exercise')
    user_id = request.form.get('user_id')

    if not video or not exercise:
        missing = []
        if not video:
            missing.append('video')
        if not exercise:
            missing.append('exercise')

        return jsonify({
            'error': 'video and exercise are required',
            'missing': missing,
            'received_files': list(request.files.keys()),
            'received_form_fields': list(request.form.keys()),
        }), 400

    os.makedirs(VIDEO_IN_DIR, exist_ok=True)
    filename = secure_filename(video.filename or 'upload.mp4')
    local_path = os.path.join(VIDEO_IN_DIR, filename)
    video.save(local_path)

    print(f"[CV] Saved upload to {local_path}, exercise={exercise}, user_id={user_id}")

    output = parse_user_video(filename, exercise, user_id)
    owner_user_id = resolve_authenticated_user_id() or str(user_id)
    asset = _create_video_asset(owner_user_id, exercise, filename)
    output['asset_id'] = asset.asset_id
    output['user_id'] = user_id
    output['exercise'] = exercise
    return jsonify(output), 200


@exercises_bp.route('/assets/<asset_id>', methods=['GET'])
def get_video_asset(asset_id):
    asset, error = _get_owned_asset_or_error(asset_id)
    if error:
        return error

    return jsonify({'asset': asset.to_dict()}), 200


@exercises_bp.route('/assets/<asset_id>/raw', methods=['GET'])
def get_raw_video_url(asset_id):
    asset, error = _get_owned_asset_or_error(asset_id)
    if error:
        return error

    url = _build_presigned_get_url(asset.raw_s3_key)
    return jsonify({
        'asset_id': asset.asset_id,
        'resource': 'raw_video',
        's3_key': asset.raw_s3_key,
        'url': url,
        'expires_in_seconds': 900,
    }), 200


@exercises_bp.route('/assets/<asset_id>/pose', methods=['GET'])
def get_pose_video_url(asset_id):
    asset, error = _get_owned_asset_or_error(asset_id)
    if error:
        return error

    url = _build_presigned_get_url(asset.pose_s3_key)
    return jsonify({
        'asset_id': asset.asset_id,
        'resource': 'pose_video',
        's3_key': asset.pose_s3_key,
        'url': url,
        'expires_in_seconds': 900,
    }), 200


# TESTING #
# This was used to ensure the parse_user_video function worked with S3, the routing WAS NOT tested, just the function. 
# if __name__ == "__main__":

#     input_video_file = 'rename.mp4'
#     exercise = 'bicep_curl'

#     overall_score, joint_scores = parse_user_video(input_video_file, exercise)
#     print(f"Overall Form Score: {overall_score}")
#     print("Joint Scores:")
#     for joint, score in joint_scores.items():
#         print(f"{joint}: {score}")