#!/usr/bin/env python3
"""
Script to check all databases and show what data is stored
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_sqlite_db():
    """Check SQLite database (users.db)"""
    print("=" * 60)
    print("SQLite Database (users.db)")
    print("=" * 60)
    
    try:
        from app.db_instance import db
        from app.auth_module.models import User
        from app.main import create_app
        
        app = create_app()
        with app.app_context():
            users = User.query.all()
            print(f"\nTotal Users: {len(users)}")
            
            if users:
                print("\nUsers:")
                for user in users:
                    print(f"  - ID: {user.id}")
                    print(f"    Username: {user.username}")
                    print(f"    Email: {user.email}")
                    print(f"    Created: {user.created_at}")
                    print()
            else:
                print("\n  No users found in SQLite database")
                print("  (Note: You're using Supabase for authentication, so this may be empty)")
    except Exception as e:
        print(f"  ❌ Error: {e}")

def check_dynamodb():
    """Check DynamoDB tables"""
    print("\n" + "=" * 60)
    print("AWS DynamoDB Tables")
    print("=" * 60)
    
    try:
        from app.dynamodb_module import (
            get_dynamodb_resource,
            USER_PROFILES_TABLE,
            HEALTH_DATA_TABLE
        )
        
        dynamodb = get_dynamodb_resource()
        
        # Check User Profiles Table
        print(f"\n📊 User Profiles Table: {USER_PROFILES_TABLE}")
        print("-" * 60)
        try:
            table = dynamodb.Table(USER_PROFILES_TABLE)
            table.load()
            
            print(f"  Status: {table.table_status}")
            print(f"  Item Count: {table.item_count}")
            
            # Scan for items (limited to first 10)
            if table.item_count > 0:
                response = table.scan(Limit=10)
                items = response.get('Items', [])
                print(f"\n  Profiles ({len(items)} shown) – user_id only; health data is in health_data table:")
                for item in items:
                    print(f"    - User ID: {item.get('user_id')}")
                    print()
            else:
                print("  No profiles found")
        except Exception as e:
            error_msg = str(e)
            if 'ResourceNotFoundException' in error_msg:
                print("  ❌ Table does not exist")
                print("     Run: python -m app.dynamodb_module.init_tables")
            else:
                print(f"  ❌ Error: {error_msg}")
        
        # Check Health Data Table
        print(f"\n📊 Health Data Table: {HEALTH_DATA_TABLE}")
        print("-" * 60)
        try:
            table = dynamodb.Table(HEALTH_DATA_TABLE)
            table.load()
            
            print(f"  Status: {table.table_status}")
            print(f"  Item Count: {table.item_count}")
            
            # Scan for items (limited to first 10)
            if table.item_count > 0:
                response = table.scan(Limit=10)
                items = response.get('Items', [])
                print(f"\n  Health Data Entries ({len(items)} shown):")
                for item in items:
                    print(f"    - User ID: {item.get('user_id')}, Timestamp: {item.get('timestamp')}")
                    if item.get('age') is not None: print(f"      Age: {item.get('age')}")
                    if item.get('height') is not None: print(f"      Height: {item.get('height')}")
                    if item.get('weight') is not None: print(f"      Weight: {item.get('weight')}")
                    if item.get('gender'): print(f"      Gender: {item.get('gender')}")
                    if item.get('fitness_goal'): print(f"      Fitness goal: {item.get('fitness_goal')}")
                    if item.get('context'): print(f"      Context: (stored)")
                    print()
            else:
                print("  No health data entries found")
        except Exception as e:
            error_msg = str(e)
            if 'ResourceNotFoundException' in error_msg:
                print("  ❌ Table does not exist")
                print("     Run: python -m app.dynamodb_module.init_tables")
            else:
                print(f"  ❌ Error: {error_msg}")
                
    except ValueError as e:
        print(f"  ❌ Configuration Error: {e}")
        print("     Make sure AWS credentials are set in .env file")
    except Exception as e:
        print(f"  ❌ Error: {e}")

def check_supabase():
    """Check Supabase (authentication)"""
    print("\n" + "=" * 60)
    print("Supabase (Authentication)")
    print("=" * 60)
    
    try:
        from app.auth_module.supabase_client import get_supabase_client
        
        supabase = get_supabase_client()
        print("\n  ✅ Supabase client configured")
        print("  ℹ️  User data is stored in Supabase cloud")
        print("  ℹ️  To view users, check your Supabase dashboard:")
        print("     https://supabase.com/dashboard")
        print("     → Your Project → Authentication → Users")
    except Exception as e:
        print(f"  ❌ Error: {e}")

def main():
    print("=" * 60)
    print("Database Contents Check")
    print("=" * 60)
    print("\nThis script checks all your databases:")
    print("  1. SQLite (local users.db)")
    print("  2. DynamoDB (user profiles & health data)")
    print("  3. Supabase (authentication)")
    
    check_sqlite_db()
    check_dynamodb()
    check_supabase()
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print("\nYour application uses:")
    print("  • Supabase: For user authentication (email/password)")
    print("  • DynamoDB: For user profiles and health data (if configured)")
    print("  • SQLite: Legacy/local storage (may be empty if using Supabase)")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()

