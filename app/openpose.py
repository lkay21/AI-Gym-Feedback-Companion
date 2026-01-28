import cv2 as cv
import os
import numpy as np
import exercise
import time
import mediapipe as mp

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

# proto_file = "./app/models/pose_deploy.prototxt"
# weights_file = "./app/models/pose_iter_440000.caffemodel"

def generate_pose(file_path, joint_group, frame_vals):

    # load the pre-trained model
    net = cv.dnn.readNetFromTensorflow("app/models/graph_opt.pb")
    thres = 0.3

    # read the video file and use opencv to gather width, height, fps
    cap = cv.VideoCapture(file_path)
    frame_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv.CAP_PROP_FPS)
    print(f"Video properties - Width: {frame_width}, Height: {frame_height}, FPS: {fps}")

    # define the codec and create video writer object (format)
    fourcc = cv.VideoWriter_fourcc(*'avc1')

    # directory to save output video and create output video writer (actual video work)
    output_path = os.path.join('app', 'video_out', os.path.basename(file_path))
    # output_path = os.path.join('static', 'pose_videos', os.path.basename(file_path))
    out = cv.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

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
                    print(f"Frame {frame_count} - Body Part {BODY_PARTS_BY_INDEX[i]}: ({int(x)}, {int(y)}) with prob {prob}")

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

    return frame_count, fps

if __name__ == "__main__":
    left_bicep_curl = exercise.Exercise.from_preset("iso_left_bicep_curl")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(script_dir, "video_in", "test.mp4")

    frame_vals = {}
    joint_group_nums = []
    
    for joint in left_bicep_curl.joint_group:
        joint_group_nums.append(exercise.BODY_PARTS[joint])
        frame_vals[joint] = {}

    for key, val in frame_vals.items():
        print(f"Initializing frame_vals for {key}: {val}")

    start_time = time.time()
    frame_count, fps  = generate_pose(video_path, joint_group_nums, frame_vals)
    end_time = time.time()

    print(f"\nTime taken for pose estimation: {end_time - start_time} seconds")

    print("\nFrames processed for pose estimation of video for Excercise")
    print(f"Exercise Name: {left_bicep_curl.name}"
        f"\nIsolated Movement: {left_bicep_curl.isolated_movement}"
        f"\nJoint Group: {left_bicep_curl.joint_group}\n")
    
    left_bicep_curl.set_frame_values(frame_vals, frame_count, fps)
    left_bicep_curl.graph_metrics()
    
    for joint in frame_vals.keys():
        print(f"Joint: {joint}")
        print(frame_vals[joint])
        print("\n")
