# API routes for handling user video uploads, pose generation, and feedback 

from flask import Blueprint, request, jsonify, session
from app.exercises.openpose import generate_pose, FormScore, fetch_standard_data, get_standard_pose
from app.exercises.exercise import Exercise, EXERCISE_PRESETS

exercises_bp = Blueprint('exercises', __name__)


# Might have to map frontend naming to EXERCISE PRESETS
@exercises_bp.route('/upload_video', methods=['POST'])
def parse_user_video(video_file, exercise):

    # video_file = check_file_type(video_file)

    # add video to storage and call formscore

    # Add to video_in
    # Call formscore with video path and exercise type
    overall_score, joint_scores = FormScore(video_file, exercise)

    return jsonify({
        "overall_score": overall_score,
        "joint_scores": joint_scores
    })

# given exercise and standard video, update standard data for exercise
@exercises_bp.route('/update_standard_data', methods=['POST'])
def update_standard_data(exercise, video_file):
    pass

# given exercise, return standard pose data for that exercise
# only callable AFTER parse_user_video has been called at least once to generate pose estimation data for the exercise
@exercises_bp.route('/get_user_pose_estimation', methods=['GET'])
def get_user_pose_estimation():
    pass
