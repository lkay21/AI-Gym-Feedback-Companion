# API routes for handling user video uploads, pose generation, and feedback 
# new branch
from flask import Blueprint, request, jsonify
import boto3
from dotenv import load_dotenv
import os
from werkzeug.utils import secure_filename
from .openpose import generate_pose, FormScore, fetch_standard_data, get_standard_pose, user_output
from .exercise import Exercise, EXERCISE_PRESETS

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

# Might have to map frontend naming to EXERCISE PRESETS
# IMPORTANT #
# Function assumes input video file is inside video_in folder within exercises directory, for final application this will likely become the following process:
# 1. User uploads video through frontend, video is sent to backend and stored in S3 bucket
# 2. Backend retrieves video from S3 bucket and stores it in video_in folder
# 3. Function processes and both video and pose estimation are in S3 bucket for frontend to retrieve and display
# 4. Delete video from local folder as any further use will occur through S3
def parse_user_video(video_file, exercise):

    # ensure coorect video file type
    # video_file = check_file_type(video_file)

    input_video_path = os.path.join('video_in', video_file)
    video_file_name = video_file + '_raw'
    # upload raw video to S3
    with open(input_video_path, 'rb') as vfile:
        s3.upload_fileobj(vfile, bucket_name, video_file_name)

    # Add to video_in
    # Call formscore with video path and exercise type
    output = user_output(video_file, exercise, aws_upload=True)
    # overall_score, joint_scores = FormScore(video_file, exercise, aws_upload=True)

    return output


@exercises_bp.route('/analyze', methods=['POST'])
def analyze_video():
    video = request.files.get('video')
    exercise = request.form.get('exercise')
    user_id = request.form.get('user_id')

    if not video or not exercise:
        return jsonify({'error': 'video and exercise are required'}), 400

    os.makedirs('video_in', exist_ok=True)
    filename = secure_filename(video.filename or 'upload.mp4')
    local_path = os.path.join('video_in', filename)
    video.save(local_path)

    output = parse_user_video(filename, exercise)

    if isinstance(output, dict):
        output['user_id'] = user_id
        output['exercise'] = exercise
        return jsonify(output), 200

    return jsonify({'result': output, 'user_id': user_id, 'exercise': exercise}), 200

# given exercise and standard video, update standard data for exercise
@exercises_bp.route('/update_standard_data', methods=['POST'])
def update_standard_data(exercise, video_file):
    pass

# given exercise, return standard pose data for that exercise
# only callable AFTER parse_user_video has been called at least once to generate pose estimation data for the exercise
@exercises_bp.route('/get_user_pose_estimation', methods=['GET'])
def get_user_pose_estimation():
    pass



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