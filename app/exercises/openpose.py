import shutil
import boto3
import cv2 as cv
import os
from dotenv import load_dotenv
import numpy as np
import exercise as ex
import time
import mediapipe as mp
from sklearn.metrics import root_mean_squared_error
from scipy.interpolate import interp1d
import subprocess
from google import genai
import os

load_dotenv()
    
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION = os.getenv('AWS_REGION')
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION)

bucket_name = 'fitness-form-videos'

# body parts and pose pairs for OpenPose (graph.opt)
BODY_PARTS = { "Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
               "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
               "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "REye": 14,
               "LEye": 15, "REar": 16, "LEar": 17, "Background": 18 }      

BODY_PARTS_BY_INDEX = { 0: "Nose", 1: "Neck", 2: "RShoulder", 3: "RElbow", 4: "RWrist",
               5: "LShoulder", 6: "LElbow", 7: "LWrist", 8: "RHip", 9: "RKnee",
               10: "RAnkle", 11: "LHip", 12: "LKnee", 13: "LAnkle", 14: "REye",
               15: "LEye", 16: "REar", 17: "LEar", 18: "Background" }             

POSE_PAIRS = [ ["Neck", "RShoulder"], ["Neck", "LShoulder"], ["RShoulder", "RElbow"],
               ["RElbow", "RWrist"], ["LShoulder", "LElbow"], ["LElbow", "LWrist"],
               ["Neck", "RHip"], ["RHip", "RKnee"], ["RKnee", "RAnkle"],
               ["Neck", "LHip"], ["LHip", "LKnee"], ["LKnee", "LAnkle"],
               ["Neck", "Nose"], ["Nose", "REye"], ["REye", "REar"],
               ["Nose", "LEye"], ["LEye", "LEar"] ]

EXERCISES = ["bicep_curl", "lateral_raise"]

APP_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(APP_DIR)
APP_DATA_DIR = os.path.join(APP_DIR, "exercise_data")

# proto_file = "./app/models/pose_deploy.prototxt"
# weights_file = "./app/models/pose_iter_440000.caffemodel"

def generate_pose(file_path, joint_group, frame_vals, aws_upload):

    # load the pre-trained model
    net = cv.dnn.readNetFromTensorflow(os.path.join(APP_DIR, "models", "graph_opt.pb"))
    thres = 0.15

    # read the video file and use opencv to gather width, height, fps
    cap = cv.VideoCapture(file_path)
    frame_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv.CAP_PROP_FPS)
    print(f"Video properties - Width: {frame_width}, Height: {frame_height}, FPS: {fps}")

    # define the codec and create video writer object (format)
    fourcc = cv.VideoWriter_fourcc(*'avc1')

    # directory to save output video and create output video writer (actual video work)

    # TODO: need to update output path to S3 compatible path and add S3 upload functionality after video is written locally
    output_path = os.path.join(APP_DIR, 'video_out', os.path.basename(file_path))
    # output_path = os.path.join('static', 'pose_videos', os.path.basename(file_path))

    print(f"Output video will be saved to: {output_path}")
    out = cv.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
    if not out.isOpened():
        print("Error: Could not open video writer.")
        return

    # read the first two frames, ret is bool if frame read and frame is frame properties
    ret, frame_1 = cap.read()
    ret, frame_2 = cap.read()

    frame_count = 0
    # loop through video frames
    while cap.isOpened():

        # select frame and get its dimensions
        frame = frame_1
        frame_height, frame_width, _ = frame.shape

        # prepare frame for dnn
        # resize to 368x368, normalize, convert BGR to RGB
        # pass the frame through the network
        net.setInput(cv.dnn.blobFromImage(frame, 1.0, (368, 368), (127.5, 127.5, 127.5), swapRB=True, crop=False))
        output = net.forward()

        # print(output.shape)


        # extract dimensions of heatmap outputted by net 
        H = output.shape[2]
        W = output.shape[3]

        points = []
        # loop through body parts and find highest confidence position of each
        for i in range(len(BODY_PARTS)):
            probMap = output[0, i, :, :]
            # prob is confidence value, point is position of body part on heatmap
            minVal, prob, minLoc, point = cv.minMaxLoc(probMap)

            # scale back to frame size
            x = (frame_width * point[0]) / W
            y = (frame_height * point[1]) / H


            # if confidence greater than the threshold add the point
            if prob > thres:
                points.append((int(x), int(y)))
                cv.circle(frame, (int(x), int(y)), 5, (0, 255, 255), thickness=-1, lineType=cv.FILLED)
                cv.putText(frame, "{}".format(i), (int(x), int(y)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, lineType=cv.LINE_AA)
                
                if i in joint_group:
                    # print(f"Frame {frame_count} - Body Part {BODY_PARTS_BY_INDEX[i]}: ({int(x)}, {int(y)}) with prob {prob}")

                    # frame_vals is dictionary of dictionaries, need to access body_part index first and then frame count
                    # if frame count does not exist, create it and then add the x,y tuple
                    if BODY_PARTS_BY_INDEX[i] in frame_vals:
                        frame_vals[BODY_PARTS_BY_INDEX[i]][frame_count] = (int(x), int(y))
                    else:
                        frame_vals[BODY_PARTS_BY_INDEX[i]] = {}
                        frame_vals[BODY_PARTS_BY_INDEX[i]][frame_count] = (int(x), int(y))
                    
            else:
                points.append(None)

        for pair in POSE_PAIRS:
            partA = pair[0]
            partB = pair[1]
            idA = BODY_PARTS[partA]
            idB = BODY_PARTS[partB]

            # if both joints exist, draw line between them
            if points[idA] and points[idB]:
                cv.line(frame, points[idA], points[idB], (0, 255, 0), 3)

        # use video writer to write the frame with pose data
        out.write(frame)

        # increment frames
        frame_1 = frame_2
        ret, frame_2 = cap.read()   

        frame_count += 1

        if not ret:
            break
        
        if cv.waitKey(40) == 27:
            break
    
    cap.release()
    out.release()
    cv.destroyAllWindows()

    if aws_upload:
        s3.upload_file(output_path, bucket_name, os.path.basename(output_path))

    return frame_count, fps, frame_width, frame_height

def fetch_standard_data(joint, axis, exercise_name):
    output_data = []
    # raw_data = {}

    # # update to use fps when velocity/acceleration needed
    # fps, frame_width, frame_height = 0, 0, 0

    folder_name = f"{exercise_name}"
    folder_name = folder_name.replace(" ", "_").lower()
    output_path = os.path.join(APP_DATA_DIR, folder_name)
    file_name = f"{exercise_name}_{joint}".replace(" ", "_").lower()
    vid_file_name = f"{exercise_name}_video_params".replace(" ", "_").lower()

    with open(os.path.join(output_path, file_name + ".txt"), 'r') as f:
        lines = f.readlines()
        raw_data = eval(lines[1])
        f.close()

    with open(os.path.join(output_path, vid_file_name + ".txt"), 'r') as f:
        lines = f.readlines()
        fps = float(lines[1].split(": ")[1])    
        frame_width = int(lines[2].split(": ")[1])
        frame_height = int(lines[3].split(": ")[1])
        f.close()

    
    ax = 0 if axis.lower() == "x" else 1
    div = frame_width if axis.lower() == "x" else frame_height

    for key, val in raw_data.items():
        output_data.append(val[ax] / div)

    return output_data

def score_func(score):
    if score >= .80 and score <= 1.0:
        return score ** 2
    elif score >= .70 and score < .80:
        return score ** 3
    else:
        return score ** 4
    

# VERY basic insight generation function, can be expanded with more specific feedback based on exercise and joint movement patterns
def generate_insights(resampled_example_x, resampled_user_x, resampled_example_y, resampled_user_y, joint, exercise_obj_name):

    insights = []

    diff = np.mean(np.abs(np.array(resampled_example_x) - np.array(resampled_user_x)))
    if diff > 0.1:
        insights.append(f"{joint}, x")
    diff = np.mean(np.abs(np.array(resampled_example_y) - np.array(resampled_user_y)))
    if diff > 0.1:
        insights.append(f"{joint}, y")

    return insights

def FormScore(user_path, exercise, aws_upload=False):

    context_dict = {}
    user_data = {}
    standard_data = {}
        
    exercise = exercise.replace(" ", "_").lower()
    exercise_obj = ex.Exercise.from_preset(exercise)

    print(f"\nCalculating FormScore for Exercise")
    print(f"Exercise Name: {exercise_obj.name}"
        f"\nIsolated Movement: {exercise_obj.isolated_movement}"
        f"\nJoint Group: {exercise_obj.joint_group}\n")

    # example_vid = os.path.join(APP_DIR, "video_in", example_path)
    user_vid = os.path.join(APP_DIR, "video_in", user_path)

    example_xs, example_ys = {}, {}
    user_xs, user_ys = {}, {}

    frame_vals = {}
    joint_group_nums = []
    
    for joint in exercise_obj.joint_group:
        joint_group_nums.append(BODY_PARTS[joint])
        frame_vals[joint] = {}

    start_time = time.time()
    frame_count, fps, frame_width, frame_height = generate_pose(user_vid, joint_group_nums, frame_vals, aws_upload)
    end_time = time.time()

    # for key, val in frame_vals.items():
    #     print(f"Initializing frame_vals for {key}: {val}")


    print(f"Time taken for FormScore estimation: {end_time - start_time} seconds")

    exercise_obj.set_frame_values(frame_vals, frame_count, fps, frame_width, frame_height)
    # exercise_obj.graph_metrics()

    for joint in frame_vals.keys():
        user_xs[joint] = exercise_obj.x_metrics[joint + " position"]
        user_ys[joint] = exercise_obj.y_metrics[joint + " position"]
        example_xs[joint] = fetch_standard_data(joint, "x", exercise)
        example_ys[joint] = fetch_standard_data(joint, "y", exercise)
        # print(f"Joint: {joint}")
        # print(frame_vals[joint])
        # print("\n")

    joint_scores = {}

    # print("\nCalculating Joint Scores:\n")

    for joint in exercise_obj.joint_group:
        example_x = example_xs[joint]
        example_y = example_ys[joint]
        user_x = user_xs[joint]
        user_y = user_ys[joint]

        user_data[joint] = {"x": user_x, "y": user_y}
        standard_data[joint] = {"x": example_x, "y": example_y}

        common = np.linspace(0, 1, 1000)
        interp_example_x = interp1d(np.linspace(0, 1, len(example_x)), example_x)
        interp_user_x = interp1d(np.linspace(0, 1, len(user_x)), user_x)
        resampled_example_x = interp_example_x(common)
        resampled_user_x = interp_user_x(common)
        mae_x = np.mean(np.abs(resampled_example_x - resampled_user_x))
        score = 1 - mae_x
        joint_scores[joint + " x"] = score_func(score)
        
        print(f"Joint: {joint} X Score: {score}")

        interp_example_y = interp1d(np.linspace(0, 1, len(example_y)), example_y)
        interp_user_y = interp1d(np.linspace(0, 1, len(user_y)), user_y)
        resampled_example_y = interp_example_y(common)
        resampled_user_y = interp_user_y(common)
        mae_y = np.mean(np.abs(resampled_example_y - resampled_user_y))
        score = 1 - mae_y
        joint_scores[joint + " y"] = score_func(score)

        context_dict[joint] = generate_insights(resampled_example_x, resampled_user_x, resampled_example_y, resampled_user_y, joint, exercise_obj.name)

        print(f"Joint: {joint} Y Score: {score}")

    overall_score = np.mean(list(joint_scores.values()))

    print(f"\nOverall Form Score for {exercise_obj.name}: {overall_score * 100} percent\n")

    return overall_score, joint_scores, context_dict, user_data, standard_data


def user_output(user_path, exercise, aws_upload=False):

    overall_score, joint_scores, context_dict, user_data, standard_data = FormScore(user_path, exercise, aws_upload)
    out_string = f"\nFeedback:\n"

    llm_prompt = f"You are acting as a fitness coach providing feedback to a user based on their performance of a one repetition of an exercise." \
                 f"The exercise performed is {exercise} and the user's overall score is {overall_score}." \
                 f"This score has been calculated by comparing data (created from CV pose estimation) from the user's video and a standard form video." \
                 f"Please provide generic feedback for the given exercise that matches the one perfomed by the user and the data provdied to you as context."\
                 f"Here is your context, "\
                 f"Overall Score: {overall_score}\n"\
                 f"Joint Scores: {joint_scores}\n"\
                 f"Insights: {context_dict}\n"\
                 f"User Joint Data: {user_data}\n"\
                 f"Standard Joint Data: {standard_data}\n"\
                 
    client = genai.Client(api_key=GEMINI_API_KEY)

    response = client.models.generate_content(
        model = "gemini-3-flash-preview",
        contents=llm_prompt,
    )


    if overall_score >= 0.9:
        out_string += "     Great job! Your form looks good overall."
    elif overall_score >= 0.8:
        out_string += "     Not bad form! However, there are some areas for improvement in your form."
    else:
        out_string += "     Your form needs work. Focus on improving your technique for better results and injury prevention."


    out_string += response.text

    return out_string

# takes in example video for input exercise to get "standard" data for each joing in define joint group for that exercise
# data gets saved to ./exercise_data 
# also saves relevant video parameters for future use
def get_standard_pose(example_path, exercise, aws_upload=False):

    print(f"\nProcessing standard pose data for Exercise")
    print(f"Exercise Name: {exercise}")

    exercise_obj = ex.Exercise.from_preset(exercise)

    example_vid = os.path.join(APP_DIR, "video_in", example_path)

    frame_vals = {}
    joint_group_nums = []


    for joint in exercise_obj.joint_group:
        joint_group_nums.append(BODY_PARTS[joint])
        frame_vals[joint] = {}

    start_time = time.time()
    frame_count, fps, frame_width, frame_height = generate_pose(example_vid, joint_group_nums, frame_vals, aws_upload)
    end_time = time.time()

    # for key, val in frame_vals.items():
    #     print(f"Initializing frame_vals for {key}: {val}")


    print(f"Time taken for Pose estimation: {end_time - start_time} seconds")

    print("\nFrames processed for pose estimation of video for Excercise")
    exercise_obj.set_frame_values(frame_vals, frame_count, fps, frame_width, frame_height)
    # exercise_obj.graph_metrics()

    folder_name = f"{exercise_obj.name}"
    folder_name = folder_name.replace(" ", "_").lower()
    output_path = os.path.join(APP_DATA_DIR, folder_name)

    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    
    os.makedirs(output_path)

    file_name = f"{exercise_obj.name}_video_params".replace(" ", "_").lower()
    file_output_path = os.path.join(output_path, file_name + ".txt")

    with open(file_output_path, 'w') as f:
         f.write(f"Frame Count: {frame_count}\n")
         f.write(f"FPS: {fps}\n")
         f.write(f"Frame Width: {frame_width}\n")
         f.write(f"Frame Height: {frame_height}\n")


    print(f"\n gathering standard pose data for joints: {exercise_obj.joint_group}\n")
    for joint in frame_vals.keys():

        file_name = f"{exercise_obj.name}_{joint}".replace(" ", "_").lower()
        file_output_path = os.path.join(output_path, file_name + ".txt")

        with open(file_output_path, 'w') as f:
             f.write(f"Joint: {joint}\n")
             f.write(f"{frame_vals[joint]}\n")
    
# def mov_to_mp4(input_path, output_path):
#     pass

if __name__ == "__main__":

    exercise_str = "bicep_curl"
    exercise_str_2 = "lateral_raise"
    example_vid = "example.mp4"
    example_vid_2 = "lat_raise_stand.mp4"
    rename_vid = "rename.mp4"
    rename_vid_2 = "lat_raise_bad.mp4"

    # vid_strings = ["hammer_curl.mp4", "shoulder_press.mp4", "bent_over_row.mp4", "lat_pulldown.mp4"]
    # exercises = ["hammer_curl", "shoulder_press", "bent_over_row", "lat_pulldown"]

    # for vid_string, exercise in zip(vid_strings, exercises):

    #     get_standard_pose(vid_string, exercise)
    
    # get_standard_pose(example_vid, exercise_str)
    # get_standard_pose(example_vid_2, exercise_str_2)

    user_out = user_output(rename_vid, exercise_str)
    print(user_out)

    # overall, joints, context_dict = FormScore(rename_vid, exercise_str)

    # print("\nContextual Feedback for User:\n")
    # for key, feedback in context_dict.items():
    #     print(f"{key}: {feedback}")


    # overall, joints = FormScore(example_vid, rename_vid, exercise_str)

    # FormScore(example_vid_2, rename_vid_2, exercise_str_2)

    # fetch_standard_data("RWrist", "x", exercise_str)

    # get_standard_pose(example_vid, exercise_str)

    # left_bicep_curl = exercise.Exercise.from_preset("iso_left_bicep_curl")
    # bicep_curl = exercise.Exercise.from_preset("bicep_curl")

    # script_dir = os.path.dirname(os.path.abspath(__file__))
    # video_path = os.path.join(script_dir, "video_in", "test.mp4")

    # bicep_path = os.path.join(script_dir, "video_in", "rename.mp4")
    # example_bicep_path = os.path.join(script_dir, "video_in", "example.mp4")

    # paths = [example_bicep_path, bicep_path, video_path]
    # exercises = [bicep_curl, bicep_curl, left_bicep_curl]


    # for path, exercise in zip(paths, exercises):

    #     frame_vals = {}
    #     joint_group_nums = []
        
    #     for joint in exercise.joint_group:
    #         joint_group_nums.append(BODY_PARTS[joint])
    #         frame_vals[joint] = {}

    #     for key, val in frame_vals.items():
    #         print(f"Initializing frame_vals for {key}: {val}")

    #     start_time = time.time()
    #     frame_count, fps, frame_width, frame_height  = generate_pose(path, joint_group_nums, frame_vals)
    #     end_time = time.time()

    #     print(f"\nTime taken for pose estimation: {end_time - start_time} seconds")

    #     print("\nFrames processed for pose estimation of video for Excercise")
    #     print(f"Exercise Name: {exercise.name}"
    #         f"\nIsolated Movement: {exercise.isolated_movement}"
    #         f"\nJoint Group: {exercise.joint_group}\n")
        
    #     exercise.set_frame_values(frame_vals, frame_count, fps, frame_width, frame_height)
    #     exercise.graph_metrics()

    #     for joint in frame_vals.keys():
    #         print(f"Joint: {joint}")
    #         print(frame_vals[joint])
    #         print("\n")
