import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d

BODY_PARTS_BY_INDEX = { 0: "Nose", 1: "Neck", 2: "RShoulder", 3: "RElbow", 4: "RWrist",
               5: "LShoulder", 6: "LElbow", 7: "LWrist", 8: "RHip", 9: "RKnee",
               10: "RAnkle", 11: "LHip", 12: "LKnee", 13: "LAnkle", 14: "REye",
               15: "LEye", 16: "REar", 17: "LEar", 18: "Background" }

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


# Presets of ALL exercises within scope
# Plan to map correctly by using same exercise variable names in frontend that can be passed
# to backend and then therefore used correctly in object instantiation
EXERCISE_PRESETS = {
    "iso_right_bicep_curl": {
        "name": "Bicep Curl",
        "isolated_movement": True,
        "joint_group": ["RShoulder", "RElbow", "RWrist"]
    }, 
    "iso_left_bicep_curl": {
        "name": "Bicep Curl",
        "isolated_movement": True,
        "joint_group": ["LShoulder", "LElbow", "LWrist"]
    },
    "bicep_curl": {
        "name": "Bicep Curl",
        "isolated_movement": False,
        "joint_group": ["RShoulder", "RElbow", "RWrist", "LShoulder", "LElbow", "LWrist"]
    },
    "lateral_raise": {
        "name": "Lateral Raise",
        "isolated_movement": False,
        "joint_group": ["RShoulder","RElbow", "RWrist", "LShoulder", "LElbow", "LWrist"]
    },
}

class Exercise:
    def __init__(self, name, joint_group, isolated_movement):
        self.name = name
        self.joint_group = joint_group
        self.isolated_movement = isolated_movement

    def set_frame_values(self, frame_vals, frame_count, fps, frame_width, frame_height):
        self.frame_vals= frame_vals     
        self.frame_count = frame_count     
        self.fps = fps
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.x_metrics = {}
        self.y_metrics = {}

        self.get_metrics()

    def noise_reduction(self):
        pass

    def get_metrics(self):
        dt = 1 / self.fps

        for joint in self.frame_vals.keys():
            x_positions = [val[0] for val in self.frame_vals[joint].values()]
            # smoothed_x = gaussian_filter1d(x_positions, sigma=0.25)
            normalized_x = [(x / self.frame_width) for x in x_positions]
            # normalized_x = normalized_x - np.mean(normalized_x)
            self.x_metrics[joint + " position"] = normalized_x
            self.x_metrics[joint + " velocity"] = np.gradient(self.x_metrics[joint + " position"], dt)
            self.x_metrics[joint + " acceleration"] = np.gradient(self.x_metrics[joint + " velocity"], dt)


            y_positions = [val[1] for val in self.frame_vals[joint].values()]
            # smoothed_y = gaussian_filter1d(y_positions, sigma=0.25)
            normalized_y = [(y / self.frame_height) for y in y_positions]
            # normalized_y = normalized_y - np.mean(normalized_y)
            self.y_metrics[joint + " position"] = normalized_y
            self.y_metrics[joint + " velocity"] = np.gradient(self.y_metrics[joint + " position"], dt)
            self.y_metrics[joint + " acceleration"] = np.gradient(self.y_metrics[joint + " velocity"], dt)

    def graph_metrics(self):

        
        for joint in self.x_metrics.keys():

            x = np.linspace(0, 1, len(self.x_metrics[joint]))
            plt.plot(x, self.x_metrics[joint], label=f'X {joint}')
            plt.axis([0, 1, -1, 1])
            plt.title(f'{joint} X Metrics for {self.name}')
            plt.show()


        for joint in self.y_metrics.keys():

            x = np.linspace(0, 1, len(self.y_metrics[joint]))
            plt.plot(x, self.y_metrics[joint], label=f'Y {joint}')
            plt.axis([0, 1, 1, -1])
            plt.title(f'{joint} Y Metrics for {self.name}')
            plt.show()

    # Example Object Instantiation -> bicep_curl = Exercise.from_preset("bicep_curl")
    @classmethod
    def from_preset(cls, key):
        data = EXERCISE_PRESETS[key]
        return cls(**data)
    
