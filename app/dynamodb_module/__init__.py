"""
DynamoDB module for AWS DynamoDB client and utilities
"""
from app.dynamodb_module.client import (
    get_dynamodb_client,
    get_dynamodb_resource,
    create_tables_if_not_exist,
    USER_PROFILES_TABLE,
    HEALTH_DATA_TABLE
)

__all__ = [
    'get_dynamodb_client',
    'get_dynamodb_resource',
    'create_tables_if_not_exist',
    'USER_PROFILES_TABLE',
    'HEALTH_DATA_TABLE'
]

