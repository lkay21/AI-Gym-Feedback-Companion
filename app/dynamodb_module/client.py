import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# DynamoDB Table Names
USER_PROFILES_TABLE = os.getenv("DYNAMODB_USER_PROFILES_TABLE", "user_profiles")
HEALTH_DATA_TABLE = os.getenv("DYNAMODB_HEALTH_DATA_TABLE", "health_data")
FITNESS_PLAN_TABLE = os.getenv("DYNAMODB_FITNESS_PLAN_TABLE", "fitness_plan")

def get_dynamodb_client():
    """Get DynamoDB client instance"""
    # IAM role-based authentication is used here via the ECS task role.
    return boto3.client('dynamodb', region_name=AWS_REGION)

def get_dynamodb_resource():
    """Get DynamoDB resource instance (higher-level API)"""
    # IAM role-based authentication is used here via the ECS task role.
    return boto3.resource('dynamodb', region_name=AWS_REGION)

def create_tables_if_not_exist():
    """Create DynamoDB tables if they don't exist"""
    dynamodb = get_dynamodb_resource()
    
    # User Profiles Table
    try:
        table = dynamodb.create_table(
            TableName=USER_PROFILES_TABLE,
            KeySchema=[
                {
                    'AttributeName': 'user_id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'user_id',
                    'AttributeType': 'S'  # String
                }
            ],
            BillingMode='PAY_PER_REQUEST'  # On-demand pricing
        )
        table.wait_until_exists()
        print(f"Table {USER_PROFILES_TABLE} created successfully")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Table {USER_PROFILES_TABLE} already exists")
        else:
            raise
    
    # Health Data Table
    try:
        table = dynamodb.create_table(
            TableName=HEALTH_DATA_TABLE,
            KeySchema=[
                {
                    'AttributeName': 'user_id',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'timestamp',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'user_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'timestamp',
                    'AttributeType': 'S'  # ISO format timestamp string
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        table.wait_until_exists()
        print(f"Table {HEALTH_DATA_TABLE} created successfully")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Table {HEALTH_DATA_TABLE} already exists")
        else:
            raise

    # Fitness Plan Table: User ID = Partition Key (HASH), Workout ID = Sort Key (RANGE)
    try:
        table = dynamodb.create_table(
            TableName=FITNESS_PLAN_TABLE,
            KeySchema=[
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},   # Primary key (partition)
                {'AttributeName': 'workout_id', 'KeyType': 'RANGE'} # Sort key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'workout_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        table.wait_until_exists()
        print(f"Table {FITNESS_PLAN_TABLE} created successfully")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Table {FITNESS_PLAN_TABLE} already exists")
        else:
            raise
