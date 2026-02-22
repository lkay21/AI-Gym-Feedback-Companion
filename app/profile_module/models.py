"""
Data models for user profiles and health data
These define the structure of data stored in DynamoDB
"""
import json
from decimal import Decimal
from typing import Optional, Dict, List, Any

class UserProfile:
    """User profile model - stores only user_id. All health data lives in HealthData (health_data table)."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for DynamoDB storage"""
        return {'user_id': self.user_id}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """Create UserProfile from DynamoDB item"""
        return cls(user_id=data.get('user_id'))


# Reserved timestamp for the per-user "health profile" record (fixed stats + fitness_goal + context)
HEALTH_PROFILE_TIMESTAMP = "health_profile"


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
        # Context for fitness-goal-specific questions (dict in memory; stored as JSON string in DynamoDB)
        self.context = context or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert health data to dictionary for DynamoDB storage. Context stored as JSON string for reliable persistence."""
        result = {
            'user_id': self.user_id,
            'timestamp': self.timestamp,
            'age': self.age,
            'height': self.height,
            'weight': self.weight,
            'gender': self.gender,
            'fitness_goal': self.fitness_goal,
            'context': json.dumps(self.context) if self.context else None
        }
        return {k: v for k, v in result.items() if v is not None}

    @classmethod
    def _parse_context(cls, raw: Any) -> Dict[str, Any]:
        """Parse context from DynamoDB (string or legacy Map)."""
        if raw is None:
            return {}
        if isinstance(raw, str):
            try:
                return json.loads(raw)
            except (TypeError, json.JSONDecodeError):
                return {}
        if isinstance(raw, dict):
            return raw
        return {}

    @classmethod
    def _number_from_dynamodb(cls, value: Any) -> Optional[float]:
        """DynamoDB returns Decimal; convert to float for Python/JSON."""
        if value is None:
            return None
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, (int, float)):
            return float(value)
        return None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HealthData':
        """Create HealthData from DynamoDB item"""
        age_val = data.get('age')
        if isinstance(age_val, Decimal):
            age_val = int(age_val)
        return cls(
            user_id=data.get('user_id'),
            timestamp=data.get('timestamp'),
            age=age_val,
            height=cls._number_from_dynamodb(data.get('height')),
            weight=cls._number_from_dynamodb(data.get('weight')),
            gender=data.get('gender'),
            fitness_goal=data.get('fitness_goal'),
            context=cls._parse_context(data.get('context'))
        )

