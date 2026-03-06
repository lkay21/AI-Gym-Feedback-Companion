from pathlib import Path
import time

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from app.exercises.exercise import EXERCISE_PRESETS
from app.exercises.openpose import user_output


exercises_bp = Blueprint("exercises", __name__)

ALLOWED_VIDEO_EXTENSIONS = {"mp4", "mov", "avi", "mkv", "webm"}


def _is_allowed_video(filename: str) -> bool:
    if "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return extension in ALLOWED_VIDEO_EXTENSIONS


@exercises_bp.route("/upload_video", methods=["POST"])
def parse_user_video():
    uploaded_video = request.files.get("video")
    exercise = (request.form.get("exercise") or "").strip()
    user_id = (request.form.get("user_id") or "").strip()

    if uploaded_video is None or not uploaded_video.filename:
        return jsonify({"success": False, "error": "Missing uploaded video file (field name: video)."}), 400

    if not exercise:
        return jsonify({"success": False, "error": "Missing exercise in form data."}), 400

    normalized_exercise = exercise.replace(" ", "_").lower()
    if normalized_exercise not in EXERCISE_PRESETS:
        return jsonify({
            "success": False,
            "error": f"Unsupported exercise '{exercise}'.",
            "supported_exercises": sorted(EXERCISE_PRESETS.keys()),
        }), 400

    safe_filename = secure_filename(uploaded_video.filename)
    if not _is_allowed_video(safe_filename):
        return jsonify({"success": False, "error": "Unsupported video file type."}), 400

    exercises_dir = Path(__file__).resolve().parent
    video_in_dir = exercises_dir / "video_in"
    video_in_dir.mkdir(parents=True, exist_ok=True)

    timestamp = int(time.time())
    user_segment = user_id or "anon"
    stored_filename = f"{user_segment}_{timestamp}_{safe_filename}"
    save_path = video_in_dir / stored_filename

    uploaded_video.save(save_path)

    try:
        feedback = user_output(stored_filename, exercise, aws_upload=False)
    except Exception as exc:
        return jsonify({"success": False, "error": f"Video processing failed: {exc}"}), 500

    return jsonify(
        {
            "success": True,
            "exercise": exercise,
            "user_id": user_id or None,
            "video_file": stored_filename,
            "user_output": feedback,
        }
    ), 200
