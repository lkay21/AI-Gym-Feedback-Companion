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
    """Check if .env file exists and has AWS credentials"""
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / '.env'
    
    if not env_path.exists():
        print("❌ Error: .env file not found!")
        print(f"   Expected location: {env_path}")
        print("\n   Please create a .env file with your AWS credentials.")
        print("   See AWS_SETUP.md or AWS_QUICK_START.md for instructions.")
        return False
    
    # Try to read and check for AWS variables
    try:
        with open(env_path, 'r') as f:
            content = f.read()
            if 'AWS_ACCESS_KEY_ID' not in content or 'AWS_SECRET_ACCESS_KEY' not in content:
                print("⚠️  Warning: .env file exists but AWS credentials not found!")
                print(f"   File location: {env_path}")
                print("\n   Please add the following to your .env file:")
                print("     AWS_REGION=us-east-1")
                print("     AWS_ACCESS_KEY_ID=your_access_key_id")
                print("     AWS_SECRET_ACCESS_KEY=your_secret_access_key")
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
    
    print("\n✓ .env file found with AWS credentials")
    print("Creating DynamoDB tables...")
    print()
    
    try:
        create_tables_if_not_exist()
        print("\n" + "=" * 60)
        print("✅ Tables created successfully!")
        print("=" * 60)
    except ValueError as e:
        # Credential validation error
        print("\n" + "=" * 60)
        print("❌ Configuration Error")
        print("=" * 60)
        print(str(e))
        sys.exit(1)
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ Error creating tables")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print("\nFull traceback:")
        import traceback
        traceback.print_exc()
        sys.exit(1)

