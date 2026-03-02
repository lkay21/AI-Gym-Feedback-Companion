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

    def test_AWS_credentials_present(self):
        self.assertIsNotNone(os.getenv('AWS_ACCESS_KEY_ID'))
        self.assertIsNotNone(os.getenv('AWS_SECRET_ACCESS_KEY'))
        self.assertIsNotNone(os.getenv('AWS_REGION'))

    @patch('app.exercises.routes.user_output')
    @patch('app.exercises.routes.s3')
    @patch('builtins.open', mock_open(read_data=b'fake_video_bytes'))
    def test_aws_video_parse(self, mock_s3, mock_user_output):

        mock_user_output.return_value = "Form looks good!"
        result = parse_user_video('test.mp4', 'bicep_curl')
        mock_s3.upload_fileobj.assert_called_once_with(ANY, 'fitness-form-videos', 'test.mp4_raw')
        
        self.assertEqual(result, "Form looks good!")


class TestFormScore(unittest.TestCase):

    pass
    # def test_get_standard_pose():
    #     pass

    # def test_user_output():
    #     pass

    # def test_formscore():
    #     pass

    # def test_generate_pose():
    #     # video = "rename.mp4"
    #     # frame_count, fps, frame_width, frame_height = gen
    #     pass


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


if __name__ == "__main__":
    unittest.main()
