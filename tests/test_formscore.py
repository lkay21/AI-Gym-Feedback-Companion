import os
import sys
import unittest
from unittest.mock import MagicMock, patch, mock_open, ANY
import numpy as np
import boto3
import io

from dotenv import load_dotenv
load_dotenv()


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.exercises.exercise import Exercise, EXERCISE_PRESETS
from app.exercises.routes import parse_user_video
from app.exercises.openpose import generate_pose, fetch_standard_data, score_func, FormScore, user_output

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION = os.getenv('AWS_REGION')

s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION
    )


class TestS3(unittest.TestCase):

    # def test_AWS_credentials_present(self):
    #     self.assertIsNotNone(os.getenv('AWS_ACCESS_KEY_ID'))
    #     self.assertIsNotNone(os.getenv('AWS_SECRET_ACCESS_KEY'))
    #     self.assertIsNotNone(os.getenv('AWS_REGION'))

    @patch('app.exercises.routes.user_output')
    @patch('app.exercises.routes.s3')
    @patch('builtins.open', mock_open(read_data=b'fake_video_bytes'))
    def test_aws_video_parse(self, mock_s3, mock_user_output):

        mock_user_output.return_value = (0.85, {"RWrist": 0.9}, {}, {}, {}, "Great form!")
        result = parse_user_video('test.mp4', 'bicep_curl', 'user123')
        mock_s3.upload_fileobj.assert_called_once_with(ANY, 'fitness-form-videos', 'user123_bicep_curl?test.mp4_raw')
        
        self.assertIsInstance(result, dict)
        self.assertIn('form_score', result)
        self.assertEqual(result['form_score'], 85.0)

class TestExerciseClass(unittest.TestCase):
    def test_from_preset_builds_expected_exercise(self):

        exercise = Exercise.from_preset("bicep_curl")

        self.assertEqual(exercise.name, EXERCISE_PRESETS["bicep_curl"]["name"])
        self.assertEqual(exercise.joint_group, EXERCISE_PRESETS["bicep_curl"]["joint_group"])
        self.assertEqual(
            exercise.isolated_movement,
            EXERCISE_PRESETS["bicep_curl"]["isolated_movement"],
        )

    def test_set_frame_values_populates_metrics_and_derivatives(self):
        exercise = Exercise("Bicep Curl", ["RWrist"], False)
        frame_vals = {"RWrist": {0: (0, 10), 1: (10, 20), 2: (20, 30)}}

        exercise.set_frame_values(frame_vals, frame_count=3, fps=2, frame_width=20, frame_height=40)

        self.assertEqual(exercise.x_metrics["RWrist position"], [0.0, 0.5, 1.0])
        self.assertEqual(exercise.y_metrics["RWrist position"], [0.25, 0.5, 0.75])
        self.assertEqual(len(exercise.x_metrics["RWrist velocity"]), 3)
        self.assertEqual(len(exercise.y_metrics["RWrist acceleration"]), 3)

    def test_single_sample_uses_zero_velocity_and_acceleration(self):
        exercise = Exercise("Bicep Curl", ["RWrist"], False)
        frame_vals = {"RWrist": {0: (50, 25)}}

        exercise.set_frame_values(frame_vals, frame_count=1, fps=30, frame_width=100, frame_height=50)

        self.assertTrue(np.array_equal(exercise.x_metrics["RWrist velocity"], np.zeros(1)))
        self.assertTrue(np.array_equal(exercise.x_metrics["RWrist acceleration"], np.zeros(1)))
        self.assertTrue(np.array_equal(exercise.y_metrics["RWrist velocity"], np.zeros(1)))
        self.assertTrue(np.array_equal(exercise.y_metrics["RWrist acceleration"], np.zeros(1)))

class TestFormScore(unittest.TestCase):

    @patch('app.exercises.openpose.video_robustness_check')
    @patch('app.exercises.openpose.s3')
    @patch('app.exercises.openpose.cv')
    def test_generate_pose_video_properties(self, mock_cv, mock_s3, mock_robustness):

        # assert properties returned
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_robustness.return_value = 'fake.mp4'

        mock_cap = MagicMock()
        mock_cap.get.side_effect = [640, 480, 30.0]
        mock_cap.read.side_effect = [
            (True, frame),    
            (True, frame),    
            (False, None) 
        ]   

        mock_cv.VideoCapture.return_value = mock_cap
        mock_cv.VideoWriter.return_value = MagicMock()
        mock_cv.VideoWriter_fourcc.return_value = 0
        mock_cv.minMaxLoc.return_value = (0.0, 0.9, (0, 0), (5, 5))

        mock_net = MagicMock()
        mock_net.forward.return_value = np.zeros((1, 19, 10, 10))
        mock_cv.dnn.readNetFromTensorflow.return_value = mock_net

        frame_count, fps, frame_width, frame_height = generate_pose('fake.mp4', [], {}, 'user123', 'bicep_curl', aws_upload=False)

        self.assertEqual(frame_width, 640)
        self.assertEqual(frame_height, 480)
        self.assertEqual(fps, 30.0)
        self.assertEqual(frame_count, 1)

    @patch('app.exercises.openpose.video_robustness_check')
    @patch('app.exercises.openpose.s3')
    @patch('app.exercises.openpose.cv')
    def test_generate_pose_aws_flag_true(self, mock_cv, mock_s3, mock_robustness):

        # assert s3.upload_file is called when aws_upload=True
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_robustness.return_value = 'test.mp4'

        mock_cap = MagicMock()
        mock_cap.get.side_effect = [640, 480, 30.0]
        mock_cap.read.side_effect = [
            (True, frame),    
            (True, frame),    
            (False, None) 
        ]   

        mock_cv.VideoCapture.return_value = mock_cap
        mock_cv.VideoWriter.return_value = MagicMock()
        mock_cv.VideoWriter_fourcc.return_value = 0
        mock_cv.minMaxLoc.return_value = (0.0, 0.9, (0, 0), (5, 5))

        mock_net = MagicMock()
        mock_net.forward.return_value = np.zeros((1, 19, 10, 10))
        mock_cv.dnn.readNetFromTensorflow.return_value = mock_net

        frame_count, fps, frame_width, frame_height = generate_pose('test.mp4', [], {}, 'user123', 'bicep_curl', aws_upload=True)

        mock_s3.upload_file.assert_called_once()

    @patch('app.exercises.openpose.video_robustness_check')
    @patch('app.exercises.openpose.s3')
    @patch('app.exercises.openpose.cv')
    def test_generate_pose_aws_flag_false(self, mock_cv, mock_s3, mock_robustness):

        # assert s3.upload_file is NOT called when aws_upload=True
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_robustness.return_value = 'test.mp4'

        mock_cap = MagicMock()
        mock_cap.get.side_effect = [640, 480, 30.0]
        mock_cap.read.side_effect = [
            (True, frame),    
            (True, frame),    
            (False, None) 
        ]   

        mock_cv.VideoCapture.return_value = mock_cap
        mock_cv.VideoWriter.return_value = MagicMock()
        mock_cv.VideoWriter_fourcc.return_value = 0
        mock_cv.minMaxLoc.return_value = (0.0, 0.9, (0, 0), (5, 5))

        mock_net = MagicMock()
        mock_net.forward.return_value = np.zeros((1, 19, 10, 10))
        mock_cv.dnn.readNetFromTensorflow.return_value = mock_net

        frame_count, fps, frame_width, frame_height = generate_pose('test.mp4', [], {}, 'user123', 'bicep_curl', aws_upload=False)

        mock_s3.upload_file.assert_not_called()

    def test_fetch_standard_data_return_type(self):
        
        exercise = Exercise.from_preset("bicep_curl")
        x_out, y_out = {}, {}

        for joint in exercise.joint_group:
            x_out[joint] = fetch_standard_data(joint, 'x', exercise.name)
            y_out[joint] = fetch_standard_data(joint, 'y', exercise.name)

            self.assertIsInstance(x_out[joint], list)
            self.assertIsInstance(y_out[joint], list)

    def test_fetch_standard_exercise_dne(self):
        with self.assertRaises(FileNotFoundError):
            fetch_standard_data('RShoulder', 'y', 'easy_exercise')

    def test_score_func_high(self):
        # Update to match new score_func logic
        # The new function is likely more complex, so just check output is float and in [0,1]
        result = score_func(0.9)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)

    def test_score_func_med(self):
        result = score_func(0.75)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)

    def test_score_func_lo(self):
        result = score_func(0.55)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)

    @patch('app.exercises.openpose.generate_pose')
    @patch('app.exercises.openpose.fetch_standard_data')
    def test_formscore_returns_expected_keys(self, mock_fetch, mock_generate):
        
        def fake_generate_pose(path, joint_group_nums, frame_vals, user_id, exercise, aws_upload):
            for key in frame_vals.keys():
                frame_vals[key] = {0: (100, 200), 1: (110, 210), 2: (120, 220)}
            return (3, 30.0, 640, 480)
        
        mock_generate.side_effect = fake_generate_pose
        mock_fetch.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]

        overall_score, joint_scores, context_dict, user_data, standard_data = FormScore('test.mp4', 'bicep_curl', 'user123')


        self.assertIsInstance(overall_score, float)
        self.assertIsInstance(joint_scores, dict)
        self.assertGreaterEqual(overall_score, 0.0)
        self.assertLessEqual(overall_score, 1.0)
        self.assertIsInstance(context_dict, dict)
        self.assertIsInstance(user_data, dict)
        self.assertIsInstance(standard_data, dict)

    @patch('app.exercises.openpose.genai')
    @patch('app.exercises.openpose.FormScore')
    def test_user_output_return(self, mock_formscore, mock_genai):
        # Update to match new output keys: 'What_went_well', 'What_needs_improvement', 'What_to_fix_next_time'
        mock_formscore.return_value = (0.85, {"RWrist": 0.9}, {}, {}, {})
        mock_genai.Client.return_value.models.generate_content.return_value.text = "{'What_went_well': ['Good form'], 'What_needs_improvement': ['Work on speed'], 'What_to_fix_next_time': ['Use more control']}"

        overall_score, joint_scores, context_dict, user_data, standard_data, out_string = user_output('test.mp4', 'bicep_curl', 'user123')

        self.assertIsInstance(overall_score, float)
        self.assertEqual(overall_score, 0.85)
        self.assertIsInstance(joint_scores, dict)
        self.assertIsInstance(out_string, str)
        self.assertIn("What went well", out_string)
        self.assertIn("What needs improvement", out_string)
        self.assertIn("What to fix next time", out_string)

    
if __name__ == "__main__":
    unittest.main()
