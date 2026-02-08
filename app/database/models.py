"""
User profile model for the AI Fitness Planner.

Defines the UserProfile dataclass that encapsulates user information
for use across the application.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


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
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    fitness_goals: List[str] = field(default_factory=list)
    # Extensibility placeholders for future features
    exercise_history: List[Dict[str, Any]] = field(default_factory=list)
    benchmarks: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Basic validation to keep the model consistent and testable."""
        if self.age is not None:
            if not isinstance(self.age, int) or self.age <= 0:
                raise ValueError("age must be a positive integer")
        if self.fitness_goals is None:
            self.fitness_goals = []
        if self.exercise_history is None:
            self.exercise_history = []
        if self.benchmarks is None:
            self.benchmarks = {}
    
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
            fitness_goals=data.get('fitness_goals', []),
            exercise_history=data.get('exercise_history', []),
            benchmarks=data.get('benchmarks', {})
        )

    @classmethod
    def create(cls, data: dict) -> "UserProfile":
        """
        Create a new user profile with basic validation.

        Args:
            data: Dictionary with user profile fields

        Returns:
            UserProfile instance
        """
        name = data.get('name')
        if not name or not isinstance(name, str):
            raise ValueError("name is required and must be a string")
        return cls.from_dict(data)

    def update(self, updates: dict) -> "UserProfile":
        """
        Update mutable fields on the profile with basic validation.

        Args:
            updates: Dictionary with fields to update

        Returns:
            Updated UserProfile instance (self)
        """
        if 'name' in updates:
            name = updates.get('name')
            if name is not None and not isinstance(name, str):
                raise ValueError("name must be a string")
            self.name = name
        if 'age' in updates:
            age = updates.get('age')
            if age is not None:
                if not isinstance(age, int) or age <= 0:
                    raise ValueError("age must be a positive integer")
            self.age = age
        if 'gender' in updates:
            self.gender = updates.get('gender')
        if 'height' in updates:
            self.height = updates.get('height')
        if 'weight' in updates:
            self.weight = updates.get('weight')
        if 'fitness_goals' in updates:
            goals = updates.get('fitness_goals')
            if goals is None:
                self.fitness_goals = []
            elif not isinstance(goals, list):
                raise ValueError("fitness_goals must be a list")
            else:
                self.fitness_goals = goals
        if 'exercise_history' in updates:
            history = updates.get('exercise_history')
            if history is None:
                self.exercise_history = []
            elif not isinstance(history, list):
                raise ValueError("exercise_history must be a list")
            else:
                self.exercise_history = history
        if 'benchmarks' in updates:
            benchmarks = updates.get('benchmarks')
            if benchmarks is None:
                self.benchmarks = {}
            elif not isinstance(benchmarks, dict):
                raise ValueError("benchmarks must be a dict")
            else:
                self.benchmarks = benchmarks
        return self
    
    def __repr__(self) -> str:
        """Return string representation of the user profile."""
        return f"UserProfile(name={self.name}, age={self.age}, gender={self.gender})"
