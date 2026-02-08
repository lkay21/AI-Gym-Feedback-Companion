"""
Lightweight data models for future FormScore integration.

These placeholders are intentionally simple and independent of scoring/biomechanics
logic. They provide typed attributes and a to_dict() method for testing/debugging.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class Joint:
    """
    Basic joint representation.

    Attributes:
        name: Human-readable joint name (e.g., "Elbow")
        index: Optional index from pose model output
        x: X coordinate (normalized or pixel)
        y: Y coordinate (normalized or pixel)
        z: Optional Z coordinate if available
        confidence: Optional confidence score
        metadata: Extra fields for future expansion
    """
    name: str
    index: Optional[int] = None
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None
    confidence: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable dictionary representation of the joint."""
        return {
            "name": self.name,
            "index": self.index,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "confidence": self.confidence,
            "metadata": dict(self.metadata),
        }


@dataclass
class JointGroup:
    """
    Group of joints representing a limb or anatomical region.

    Attributes:
        name: Group name (e.g., "RightArm")
        joints: Joints included in the group
        metadata: Extra fields for future expansion
    """
    name: str
    joints: List[Joint] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable dictionary representation of the joint group."""
        return {
            "name": self.name,
            "joints": [joint.to_dict() for joint in self.joints],
            "metadata": dict(self.metadata),
        }


@dataclass
class Exercise:
    """
    Exercise definition placeholder for FormScore integration.

    Attributes:
        name: Exercise name (e.g., "Squat")
        joint_groups: Joint groups relevant to the exercise
        primary_joints: Optional list of primary joints by name
        metadata: Extra fields for future expansion
    """
    name: str
    joint_groups: List[JointGroup] = field(default_factory=list)
    primary_joints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable dictionary representation of the exercise."""
        return {
            "name": self.name,
            "joint_groups": [group.to_dict() for group in self.joint_groups],
            "primary_joints": list(self.primary_joints),
            "metadata": dict(self.metadata),
        }
