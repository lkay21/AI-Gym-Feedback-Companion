#!/usr/bin/env python3
"""
Helper script to check .env file configuration
Safely displays which environment variables are set (without exposing secrets)
"""
import os
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent
env_path = project_root / '.env'

print("=" * 60)
print("Environment Configuration Check")
print("=" * 60)

# Check if .env file exists
if not env_path.exists():
    print(f"\n❌ .env file not found at: {env_path}")
    print("\nPlease create a .env file with the following variables:")
    print("  AWS_REGION=us-east-1")
    print("  AWS_ACCESS_KEY_ID=your_access_key_id")
    print("  AWS_SECRET_ACCESS_KEY=your_secret_access_key")
    print("  SUPABASE_URL=your_supabase_url")
    print("  SUPABASE_ANON_KEY=your_supabase_key")
    print("  GEMINI_API_KEY=your_gemini_key")
    print("  SECRET_KEY=your_secret_key")
    exit(1)

print(f"\n✓ .env file found at: {env_path}")

# Load environment variables
load_dotenv(dotenv_path=env_path)

# Check required variables
required_vars = {
    'AWS_REGION': 'AWS Region',
    'AWS_ACCESS_KEY_ID': 'AWS Access Key ID',
    'AWS_SECRET_ACCESS_KEY': 'AWS Secret Access Key',
    'SUPABASE_URL': 'Supabase URL',
    'SUPABASE_ANON_KEY': 'Supabase Anon Key',
    'GEMINI_API_KEY': 'Gemini API Key',
    'SECRET_KEY': 'Flask Secret Key'
}

optional_vars = {
    'DYNAMODB_USER_PROFILES_TABLE': 'DynamoDB User Profiles Table',
    'DYNAMODB_HEALTH_DATA_TABLE': 'DynamoDB Health Data Table'
}

print("\nRequired Variables:")
print("-" * 60)
all_required_set = True
for var, description in required_vars.items():
    value = os.getenv(var)
    if value:
        # Mask sensitive values
        if 'SECRET' in var or 'KEY' in var or 'PASSWORD' in var:
            if len(value) > 8:
                display = value[:4] + '...' + value[-4:]
            else:
                display = '***'
        else:
            display = value
        print(f"  ✓ {var:30} = {display}")
    else:
        print(f"  ❌ {var:30} = NOT SET")
        all_required_set = False

print("\nOptional Variables:")
print("-" * 60)
for var, description in optional_vars.items():
    value = os.getenv(var, 'Using default')
    print(f"  • {var:30} = {value}")

print("\n" + "=" * 60)
if all_required_set:
    print("✅ All required variables are set!")
    print("\nYou can now run:")
    print("  python -m app.dynamodb_module.init_tables")
else:
    print("❌ Some required variables are missing!")
    print("\nPlease add the missing variables to your .env file.")
print("=" * 60)

