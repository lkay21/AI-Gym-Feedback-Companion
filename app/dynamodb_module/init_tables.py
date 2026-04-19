"""
Utility script to initialize DynamoDB tables
Run this script once to create the necessary tables in DynamoDB

Usage:
    python -m app.dynamodb_module.init_tables
"""
import sys
from pathlib import Path
from app.dynamodb_module.client import create_tables_if_not_exist

def check_env_file():
    """Check whether the environment is configured for table creation."""
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / '.env'
    
    if not env_path.exists():
        print("❌ Error: .env file not found!")
        print(f"   Expected location: {env_path}")
        print("\n   Please create a .env file with configuration values such as AWS_REGION.")
        print("   ECS tasks should use the task role for AWS authentication.")
        return False

    # Try to read and check for the region configuration used by boto3.
    try:
        with open(env_path, 'r') as f:
            content = f.read()
            if 'AWS_REGION' not in content:
                print("⚠️  Warning: .env file exists but AWS_REGION was not found!")
                print(f"   File location: {env_path}")
                print("\n   Please add AWS_REGION so boto3 can target the correct region.")
                print("   AWS credentials should come from the ECS task role.")
                return False
    except Exception as e:
        print(f"⚠️  Warning: Could not read .env file: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("DynamoDB Table Initialization")
    print("=" * 60)
    
    # Check .env file first
    if not check_env_file():
        print("\n❌ Setup incomplete. Please configure your .env file first.")
        sys.exit(1)
    
    print("\n✓ Environment file found with configuration values")
    print("Creating DynamoDB tables...")
    print()
    
    try:
        create_tables_if_not_exist()
        print("\n" + "=" * 60)
        print("✅ Tables created successfully!")
        print("=" * 60)
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ Error creating tables")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print("\nFull traceback:")
        import traceback
        traceback.print_exc()
        sys.exit(1)

