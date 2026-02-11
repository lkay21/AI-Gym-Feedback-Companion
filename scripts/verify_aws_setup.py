#!/usr/bin/env python3
"""
Script to verify AWS DynamoDB setup
Run this after configuring your .env file to check if everything is set up correctly
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_env_file():
    """Check if .env file exists"""
    env_path = project_root / '.env'
    if not env_path.exists():
        print("❌ .env file not found!")
        print("   Create a .env file in the project root with your AWS credentials.")
        return False
    print("✓ .env file found")
    return True

def check_env_variables():
    """Check if required environment variables are set"""
    from dotenv import load_dotenv
    env_path = project_root / '.env'
    load_dotenv(dotenv_path=env_path)
    
    required_vars = {
        'AWS_REGION': os.getenv('AWS_REGION'),
        'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
    }
    
    optional_vars = {
        'DYNAMODB_USER_PROFILES_TABLE': os.getenv('DYNAMODB_USER_PROFILES_TABLE', 'user_profiles'),
        'DYNAMODB_HEALTH_DATA_TABLE': os.getenv('DYNAMODB_HEALTH_DATA_TABLE', 'health_data'),
    }
    
    all_good = True
    print("\nRequired Environment Variables:")
    for var, value in required_vars.items():
        if value:
            # Mask sensitive values
            if 'SECRET' in var or 'KEY' in var:
                display_value = value[:4] + '...' + value[-4:] if len(value) > 8 else '***'
            else:
                display_value = value
            print(f"  ✓ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: NOT SET")
            all_good = False
    
    print("\nOptional Environment Variables (using defaults if not set):")
    for var, value in optional_vars.items():
        print(f"  • {var}: {value}")
    
    return all_good

def check_dynamodb_connection():
    """Check if DynamoDB connection works"""
    try:
        from app.dynamodb_module import get_dynamodb_resource, USER_PROFILES_TABLE, HEALTH_DATA_TABLE
        
        print("\nTesting DynamoDB Connection...")
        dynamodb = get_dynamodb_resource()
        
        # Test user_profiles table
        try:
            table = dynamodb.Table(USER_PROFILES_TABLE)
            table.load()
            print(f"  ✓ Connected to '{USER_PROFILES_TABLE}' table")
            print(f"    Status: {table.table_status}")
            print(f"    Item count: {table.item_count}")
        except Exception as e:
            print(f"  ❌ Error accessing '{USER_PROFILES_TABLE}' table: {e}")
            print(f"    Make sure the table exists. Run: python -m app.dynamodb_module.init_tables")
            return False
        
        # Test health_data table
        try:
            table = dynamodb.Table(HEALTH_DATA_TABLE)
            table.load()
            print(f"  ✓ Connected to '{HEALTH_DATA_TABLE}' table")
            print(f"    Status: {table.table_status}")
            print(f"    Item count: {table.item_count}")
        except Exception as e:
            print(f"  ❌ Error accessing '{HEALTH_DATA_TABLE}' table: {e}")
            print(f"    Make sure the table exists. Run: python -m app.dynamodb_module.init_tables")
            return False
        
        return True
    except Exception as e:
        print(f"  ❌ Error connecting to DynamoDB: {e}")
        print("    Check your AWS credentials and region configuration")
        return False

def main():
    print("=" * 60)
    print("AWS DynamoDB Setup Verification")
    print("=" * 60)
    
    checks = []
    
    # Check 1: .env file exists
    checks.append(("Environment File", check_env_file()))
    
    if not checks[-1][1]:
        print("\n❌ Setup incomplete. Please create a .env file first.")
        sys.exit(1)
    
    # Check 2: Environment variables
    checks.append(("Environment Variables", check_env_variables()))
    
    if not checks[-1][1]:
        print("\n❌ Setup incomplete. Please set required environment variables.")
        sys.exit(1)
    
    # Check 3: DynamoDB connection
    checks.append(("DynamoDB Connection", check_dynamodb_connection()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    all_passed = True
    for check_name, result in checks:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status}: {check_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All checks passed! Your AWS setup is complete.")
        print("\nNext steps:")
        print("  1. Start your Flask application: python -m app.main")
        print("  2. Test the API endpoints")
    else:
        print("\n⚠️  Some checks failed. Please review the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()

