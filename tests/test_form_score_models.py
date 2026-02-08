"""
Unit tests for FormScore placeholder models.

Tests cover:
- Default values
- Nested structures
- to_dict() output
"""

import unittest
from app.form_score.models import Exercise, Joint, JointGroup


class TestJoint(unittest.TestCase):
    """Test Joint model."""

    def test_joint_defaults(self):
        """Test default optional values."""
        joint = Joint(name="Elbow")

        self.assertEqual(joint.name, "Elbow")
        self.assertIsNone(joint.index)
        self.assertIsNone(joint.x)
        self.assertIsNone(joint.y)
        self.assertIsNone(joint.z)
        self.assertIsNone(joint.confidence)
        self.assertEqual(joint.metadata, {})

    def test_joint_to_dict(self):
        """Test Joint to_dict() output."""
        joint = Joint(
            name="Knee",
            index=9,
            x=0.5,
            y=0.75,
            z=0.1,
            confidence=0.95,
            metadata={"side": "right"}
        )

        data = joint.to_dict()

        self.assertEqual(data["name"], "Knee")
        self.assertEqual(data["index"], 9)
        self.assertEqual(data["x"], 0.5)
        self.assertEqual(data["y"], 0.75)
        self.assertEqual(data["z"], 0.1)
        self.assertEqual(data["confidence"], 0.95)
        self.assertEqual(data["metadata"], {"side": "right"})


class TestJointGroup(unittest.TestCase):
    """Test JointGroup model."""

    def test_joint_group_defaults(self):
        """Test default values for JointGroup."""
        group = JointGroup(name="RightArm")

        self.assertEqual(group.name, "RightArm")
        self.assertEqual(group.joints, [])
        self.assertEqual(group.metadata, {})

    def test_joint_group_to_dict(self):
        """Test JointGroup to_dict() with nested joints."""
        joints = [Joint(name="Shoulder"), Joint(name="Elbow")]
        group = JointGroup(name="RightArm", joints=joints, metadata={"side": "right"})

        data = group.to_dict()

        self.assertEqual(data["name"], "RightArm")
        self.assertEqual(len(data["joints"]), 2)
        self.assertEqual(data["joints"][0]["name"], "Shoulder")
        self.assertEqual(data["joints"][1]["name"], "Elbow")
        self.assertEqual(data["metadata"], {"side": "right"})


class TestExercise(unittest.TestCase):
    """Test Exercise model."""

    def test_exercise_defaults(self):
        """Test default values for Exercise."""
        exercise = Exercise(name="Squat")

        self.assertEqual(exercise.name, "Squat")
        self.assertEqual(exercise.joint_groups, [])
        self.assertEqual(exercise.primary_joints, [])
        self.assertEqual(exercise.metadata, {})

    def test_exercise_to_dict(self):
        """Test Exercise to_dict() with nested joint groups."""
        knee = Joint(name="Knee")
        hip = Joint(name="Hip")
        legs = JointGroup(name="Legs", joints=[knee, hip])

        exercise = Exercise(
            name="Squat",
            joint_groups=[legs],
            primary_joints=["Hip", "Knee"],
            metadata={"difficulty": "beginner"}
        )

        data = exercise.to_dict()

        self.assertEqual(data["name"], "Squat")
        self.assertEqual(len(data["joint_groups"]), 1)
        self.assertEqual(data["joint_groups"][0]["name"], "Legs")
        self.assertEqual(data["joint_groups"][0]["joints"][0]["name"], "Knee")
        self.assertEqual(data["primary_joints"], ["Hip", "Knee"])
        self.assertEqual(data["metadata"], {"difficulty": "beginner"})


if __name__ == "__main__":
    unittest.main()
