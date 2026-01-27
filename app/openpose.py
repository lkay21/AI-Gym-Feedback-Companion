import cv2 as cv
import os
import numpy as np

# body parts and pose pairs for OpenPose
BODY_PARTS = { "Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
               "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
               "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "REye": 14,
               "LEye": 15, "REar": 16, "LEar": 17, "Background": 18 }                   

POSE_PAIRS = [ ["Neck", "RShoulder"], ["Neck", "LShoulder"], ["RShoulder", "RElbow"],
               ["RElbow", "RWrist"], ["LShoulder", "LElbow"], ["LElbow", "LWrist"],
               ["Neck", "RHip"], ["RHip", "RKnee"], ["RKnee", "RAnkle"],
               ["Neck", "LHip"], ["LHip", "LKnee"], ["LKnee", "LAnkle"],
               ["Neck", "Nose"], ["Nose", "REye"], ["REye", "REar"],
               ["Nose", "LEye"], ["LEye", "LEar"] ]

def generate_pose(file_path):

    # load the pre-trained model
    net = cv.dnn.readNetFromTensorflow("app/graph_opt.pb")
    thres = 0.2

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
                # print(f"Body Part {i}: ({int(x)}, {int(y)}) with prob {prob}")
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

        if not ret:
            break
        
        if cv.waitKey(40) == 27:
            break
    
    cap.release()
    out.release()
    cv.destroyAllWindows()


# def process_video(file_path, file_name):
#     cap = cv.VideoCapture(file_path)

#     frame_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
#     frame_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
#     fps = cap.get(cv.CAP_PROP_FPS)
#     fourcc = cv.VideoWriter_fourcc(*'avc1')

#     output_path = os.path.join('static', 'tracked_videos', file_name)
#     out = cv.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

#     ret, frame_1 = cap.read()
#     ret, frame_2 = cap.read()

#     while cap.isOpened():

#         diff = cv.absdiff(frame_1, frame_2)
#         gray = cv.cvtColor(diff, cv.COLOR_BGR2GRAY)
#         blur = cv.GaussianBlur(gray, (5, 5), 0)
#         _, thresh = cv.threshold(blur, 20, 255, cv.THRESH_BINARY)
#         dilated = cv.dilate(thresh, None, iterations=3)
#         contours, _ = cv.findContours(dilated, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        
#         for contour in contours:
#             if cv.contourArea(contour) < 900:
#                 continue
#             (x, y, w, h) = cv.boundingRect(contour)
#             cv.rectangle(frame_1, (x, y), (x + w, y + h), (0, 255, 0), 2)

#         out.write(frame_1)

#         # cv.imshow("Original Frame", frame_1)

#         frame_1 = frame_2
#         ret, frame_2 = cap.read()   

#         if not ret:
#             break
        
#         if cv.waitKey(40) == 27:
#             break

#     cap.release()
#     out.release()
#     cv.destroyAllWindows()

#     return file_name

if __name__ == "__main__":
    video_path = r"C:\Users\logan\SD\AI-Gym-Feedback-Companion\app\video_in\dance.mp4"
    # video_path = "AI-Gym-Feedback-Companion/app/video_in/dance.mp4"
    generate_pose(video_path)