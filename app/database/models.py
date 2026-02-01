"""
User profile model for the AI Fitness Planner.

Defines the UserProfile dataclass that encapsulates user information
for use across the application.
"""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class UserProfile:
    """
    Structured user profile object containing fitness and personal information.
    
    Attributes:
        name: User's name
        age: User's age in years
        gender: User's gender
        height: User's height (e.g., "5'10\"" or "178 cm")
        weight: User's weight (e.g., "180 lbs" or "82 kg")
        fitness_goals: List of fitness goals (e.g., ["lose weight", "build muscle"])
    """
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    fitness_goals: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: dict) -> "UserProfile":
        """
        Create a UserProfile instance from a dictionary.
        
        Args:
            data: Dictionary with user profile fields
            
        Returns:
            UserProfile instance
        """
        return cls(
            name=data.get('name'),
            age=data.get('age'),
            gender=data.get('gender'),
            height=data.get('height'),
            weight=data.get('weight'),
            fitness_goals=data.get('fitness_goals', [])
        )
    
    def __repr__(self) -> str:
        """Return string representation of the user profile."""
        return f"UserProfile(name={self.name}, age={self.age}, gender={self.gender})"
