"""
Service layer for CRUD operations on user profiles and health data
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from botocore.exceptions import ClientError
from app.dynamodb_module import get_dynamodb_resource, USER_PROFILES_TABLE, HEALTH_DATA_TABLE
from app.profile_module.models import UserProfile, HealthData


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
        """Update user profile with partial updates"""
        try:
            # Add updated_at timestamp
            updates['updated_at'] = datetime.utcnow().isoformat()
            
            # Build update expression
            update_expression_parts = []
            expression_attribute_names = {}
            expression_attribute_values = {}
            
            for key, value in updates.items():
                if key == 'user_id':
                    continue  # Skip user_id as it's the key
                
                placeholder = f"#{key}"
                value_placeholder = f":{key}"
                
                update_expression_parts.append(f"{placeholder} = {value_placeholder}")
                expression_attribute_names[placeholder] = key
                expression_attribute_values[value_placeholder] = value
            
            update_expression = "SET " + ", ".join(update_expression_parts)
            
            # Handle fitness_goals as a list
            if 'fitness_goals' in updates:
                expression_attribute_values[":fitness_goals"] = updates['fitness_goals']
            
            response = self.table.update_item(
                Key={'user_id': user_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            )
            
            return UserProfile.from_dict(response['Attributes'])
        except ClientError as e:
            raise Exception(f"Failed to update profile: {str(e)}")
    
    def delete_profile(self, user_id: str) -> bool:
        """Delete user profile"""
        try:
            self.table.delete_item(Key={'user_id': user_id})
            return True
        except ClientError as e:
            raise Exception(f"Failed to delete profile: {str(e)}")


class HealthDataService:
    """Service for health data operations"""
    
    def __init__(self):
        self.dynamodb = get_dynamodb_resource()
        self.table = self.dynamodb.Table(HEALTH_DATA_TABLE)
    
    def create_health_data(self, health_data: HealthData) -> HealthData:
        """Create a new health data entry"""
        try:
            item = health_data.to_dict()
            # Ensure timestamp is set
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
                expression_attribute_values[value_placeholder] = value
            
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

