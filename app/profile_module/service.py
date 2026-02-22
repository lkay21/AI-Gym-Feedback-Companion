"""
Service layer for CRUD operations on user profiles and health data
"""
import json
from decimal import Decimal
from typing import Optional, List, Dict, Any
from datetime import datetime
from botocore.exceptions import ClientError
from app.dynamodb_module import get_dynamodb_resource, USER_PROFILES_TABLE, HEALTH_DATA_TABLE
from app.profile_module.models import UserProfile, HealthData, HEALTH_PROFILE_TIMESTAMP


class ProfileService:
    """Service for user profile operations"""
    
    def __init__(self):
        self.dynamodb = get_dynamodb_resource()
        self.table = self.dynamodb.Table(USER_PROFILES_TABLE)
    
    def create_profile(self, profile: UserProfile) -> UserProfile:
        """Create a new user profile"""
        try:
            item = profile.to_dict()
            self.table.put_item(Item=item)
            return profile
        except ClientError as e:
            raise Exception(f"Failed to create profile: {str(e)}")
    
    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by user_id"""
        try:
            response = self.table.get_item(
                Key={'user_id': user_id}
            )
            
            if 'Item' in response:
                item = response['Item']
                return UserProfile.from_dict(item)
            return None
        except ClientError as e:
            raise Exception(f"Failed to get profile: {str(e)}")
    
    def update_profile(self, user_id: str, updates: Dict[str, Any]) -> UserProfile:
        """Profile stores only user_id; no fields to update. Ensures profile exists and returns it."""
        existing = self.get_profile(user_id)
        if existing:
            return existing
        self.create_profile(UserProfile(user_id=user_id))
        return self.get_profile(user_id)
    
    def delete_profile(self, user_id: str) -> bool:
        """Delete user profile"""
        try:
            self.table.delete_item(Key={'user_id': user_id})
            return True
        except ClientError as e:
            raise Exception(f"Failed to delete profile: {str(e)}")


def _decimalize_for_dynamodb(obj: Any) -> Any:
    """Convert float to Decimal for DynamoDB; leave other types unchanged."""
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: _decimalize_for_dynamodb(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_decimalize_for_dynamodb(x) for x in obj]
    return obj


class HealthDataService:
    """Service for health data operations"""
    
    def __init__(self):
        self.dynamodb = get_dynamodb_resource()
        self.table = self.dynamodb.Table(HEALTH_DATA_TABLE)
    
    def create_health_data(self, health_data: HealthData) -> HealthData:
        """Create a new health data entry"""
        try:
            item = _decimalize_for_dynamodb(health_data.to_dict())
            if not item.get('timestamp'):
                item['timestamp'] = datetime.utcnow().isoformat()
            
            self.table.put_item(Item=item)
            return health_data
        except ClientError as e:
            raise Exception(f"Failed to create health data: {str(e)}")
    
    def get_health_data(self, user_id: str, timestamp: str) -> Optional[HealthData]:
        """Get specific health data entry by user_id and timestamp"""
        try:
            response = self.table.get_item(
                Key={
                    'user_id': user_id,
                    'timestamp': timestamp
                }
            )
            
            if 'Item' in response:
                return HealthData.from_dict(response['Item'])
            return None
        except ClientError as e:
            raise Exception(f"Failed to get health data: {str(e)}")
    
    def get_user_health_data(
        self,
        user_id: str,
        limit: int = 100,
        start_timestamp: Optional[str] = None,
        end_timestamp: Optional[str] = None
    ) -> List[HealthData]:
        """Get all health data entries for a user, optionally filtered by time range"""
        try:
            # Build query parameters
            query_params = {
                'KeyConditionExpression': 'user_id = :user_id',
                'ExpressionAttributeValues': {
                    ':user_id': user_id
                },
                'ScanIndexForward': False,  # Most recent first
                'Limit': limit
            }
            
            # Add time range filter if provided
            if start_timestamp or end_timestamp:
                condition_parts = []
                if start_timestamp:
                    condition_parts.append('timestamp >= :start_time')
                    query_params['ExpressionAttributeValues'][':start_time'] = start_timestamp
                if end_timestamp:
                    condition_parts.append('timestamp <= :end_time')
                    query_params['ExpressionAttributeValues'][':end_time'] = end_timestamp
                
                if condition_parts:
                    query_params['KeyConditionExpression'] += ' AND ' + ' AND '.join(condition_parts)
            
            response = self.table.query(**query_params)
            
            return [HealthData.from_dict(item) for item in response.get('Items', [])]
        except ClientError as e:
            raise Exception(f"Failed to get user health data: {str(e)}")
    
    def update_health_data(
        self,
        user_id: str,
        timestamp: str,
        updates: Dict[str, Any]
    ) -> HealthData:
        """Update health data entry"""
        try:
            # Build update expression
            update_expression_parts = []
            expression_attribute_names = {}
            expression_attribute_values = {}
            
            for key, value in updates.items():
                if key in ['user_id', 'timestamp']:
                    continue  # Skip keys
                
                placeholder = f"#{key}"
                value_placeholder = f":{key}"
                
                update_expression_parts.append(f"{placeholder} = {value_placeholder}")
                expression_attribute_names[placeholder] = key
                expression_attribute_values[value_placeholder] = _decimalize_for_dynamodb(value)
            
            if not update_expression_parts:
                raise ValueError("No updates provided")
            
            update_expression = "SET " + ", ".join(update_expression_parts)
            
            response = self.table.update_item(
                Key={
                    'user_id': user_id,
                    'timestamp': timestamp
                },
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            )
            
            return HealthData.from_dict(response['Attributes'])
        except ClientError as e:
            raise Exception(f"Failed to update health data: {str(e)}")
    
    def delete_health_data(self, user_id: str, timestamp: str) -> bool:
        """Delete health data entry"""
        try:
            self.table.delete_item(
                Key={
                    'user_id': user_id,
                    'timestamp': timestamp
                }
            )
            return True
        except ClientError as e:
            raise Exception(f"Failed to delete health data: {str(e)}")

    def get_health_profile(self, user_id: str) -> Optional[HealthData]:
        """Get the user's health profile record (fixed stats + fitness_goal + context)."""
        return self.get_health_data(user_id, HEALTH_PROFILE_TIMESTAMP)

    def create_or_update_health_profile(
        self,
        user_id: str,
        age: Optional[int] = None,
        height: Optional[float] = None,
        weight: Optional[float] = None,
        gender: Optional[str] = None,
        fitness_goal: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> HealthData:
        """Create or update the health profile record (fixed stats, fitness_goal, context)."""
        existing = self.get_health_profile(user_id)
        updates = {}
        if age is not None:
            updates['age'] = age
        if height is not None:
            updates['height'] = height
        if weight is not None:
            updates['weight'] = weight
        if gender is not None:
            updates['gender'] = gender
        if fitness_goal is not None:
            updates['fitness_goal'] = fitness_goal
        if context is not None:
            # Store context as JSON string in DynamoDB for reliable persistence
            updates['context'] = json.dumps(context) if isinstance(context, dict) else context
        if existing:
            if updates:
                return self.update_health_data(user_id, HEALTH_PROFILE_TIMESTAMP, updates)
            return existing
        health_data = HealthData(
            user_id=user_id,
            timestamp=HEALTH_PROFILE_TIMESTAMP,
            age=age,
            height=height,
            weight=weight,
            gender=gender,
            fitness_goal=fitness_goal,
            context=context or {},
        )
        self.create_health_data(health_data)
        return health_data

