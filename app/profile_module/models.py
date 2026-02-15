"""
Data models for user profiles and health data
These define the structure of data stored in DynamoDB
"""
from datetime import datetime
from typing import Optional, Dict, List, Any

class UserProfile:
    """User profile model"""
    
    def __init__(
        self,
        user_id: str,
        age: Optional[int] = None,
        height: Optional[float] = None,  # in cm or inches
        weight: Optional[float] = None,  # in kg or lbs
        fitness_goals: Optional[List[str]] = None,
        gender: Optional[str] = None,
        activity_level: Optional[str] = None,  # e.g., "sedentary", "moderate", "active"
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None
    ):
        self.user_id = user_id
        self.age = age
        self.height = height
        self.weight = weight
        self.fitness_goals = fitness_goals or []
        self.gender = gender
        self.activity_level = activity_level
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for DynamoDB storage"""
        return {
            'user_id': self.user_id,
            'age': self.age,
            'height': self.height,
            'weight': self.weight,
            'fitness_goals': self.fitness_goals,
            'gender': self.gender,
            'activity_level': self.activity_level,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """Create UserProfile from DynamoDB item"""
        return cls(
            user_id=data.get('user_id'),
            age=data.get('age'),
            height=data.get('height'),
            weight=data.get('weight'),
            fitness_goals=data.get('fitness_goals', []),
            gender=data.get('gender'),
            activity_level=data.get('activity_level'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )


class HealthData:
    """Health data model with fixed health fields and context for fitness-goal-specific Q&A"""
    
    def __init__(
        self,
        user_id: str,
        timestamp: str,  # ISO format timestamp
        # Fixed health data fields
        age: Optional[int] = None,
        height: Optional[float] = None,  # in cm or inches
        weight: Optional[float] = None,  # in kg or lbs
        gender: Optional[str] = None,
        fitness_goal: Optional[str] = None,  # Primary fitness goal
        # Context field for fitness-goal-specific Q&A
        context: Optional[Dict[str, Any]] = None  # Q&A tailored to fitness goal
    ):
        self.user_id = user_id
        self.timestamp = timestamp
        # Fixed health data
        self.age = age
        self.height = height
        self.weight = weight
        self.gender = gender
        self.fitness_goal = fitness_goal
        # Context for fitness-goal-specific questions
        self.context = context or {}  # Format: {"question": "answer", ...} or {"questions": [{"q": "...", "a": "..."}]}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert health data to dictionary for DynamoDB storage"""
        result = {
            'user_id': self.user_id,
            'timestamp': self.timestamp,
            # Fixed health data fields
            'age': self.age,
            'height': self.height,
            'weight': self.weight,
            'gender': self.gender,
            'fitness_goal': self.fitness_goal,
            # Context field for fitness-goal-specific Q&A
            'context': self.context if self.context else None
        }
        
        # Remove None values
        return {k: v for k, v in result.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HealthData':
        """Create HealthData from DynamoDB item"""
        return cls(
            user_id=data.get('user_id'),
            timestamp=data.get('timestamp'),
            # Fixed health data fields
            age=data.get('age'),
            height=data.get('height'),
            weight=data.get('weight'),
            gender=data.get('gender'),
            fitness_goal=data.get('fitness_goal'),
            # Context field
            context=data.get('context', {})
        )

