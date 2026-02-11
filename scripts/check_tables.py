#!/usr/bin/env python3
"""
Script to check DynamoDB tables status
Verifies that tables exist and displays their information
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_tables():
    """Check DynamoDB tables"""
    try:
        from app.dynamodb_module import (
            get_dynamodb_resource,
            USER_PROFILES_TABLE,
            HEALTH_DATA_TABLE
        )
        
        print("=" * 60)
        print("DynamoDB Tables Status")
        print("=" * 60)
        
        dynamodb = get_dynamodb_resource()
        
        tables_to_check = [
            (USER_PROFILES_TABLE, "User Profiles"),
            (HEALTH_DATA_TABLE, "Health Data")
        ]
        
        all_exist = True
        
        for table_name, description in tables_to_check:
            print(f"\n📊 {description} Table: {table_name}")
            print("-" * 60)
            
            try:
                table = dynamodb.Table(table_name)
                table.load()  # This will raise an error if table doesn't exist
                
                # Get table details
                print(f"  ✓ Status: {table.table_status}")
                print(f"  ✓ Item Count: {table.item_count}")
                print(f"  ✓ Creation Date: {table.creation_date_time}")
                print(f"  ✓ Billing Mode: {table.billing_mode_summary.get('BillingMode', 'N/A')}")
                
                # Display key schema
                if hasattr(table, 'key_schema'):
                    print(f"  ✓ Key Schema:")
                    for key in table.key_schema:
                        print(f"      - {key['AttributeName']} ({key['KeyType']})")
                
            except Exception as e:
                error_msg = str(e)
                if 'ResourceNotFoundException' in error_msg or 'does not exist' in error_msg:
                    print(f"  ❌ Table does not exist")
                    print(f"     Run: python -m app.dynamodb_module.init_tables")
                    all_exist = False
                else:
                    print(f"  ❌ Error accessing table: {error_msg}")
                    all_exist = False
        
        print("\n" + "=" * 60)
        if all_exist:
            print("✅ All tables exist and are accessible!")
        else:
            print("❌ Some tables are missing or inaccessible")
            print("\nTo create missing tables, run:")
            print("  python -m app.dynamodb_module.init_tables")
        print("=" * 60)
        
        return all_exist
        
    except ValueError as e:
        print("=" * 60)
        print("❌ Configuration Error")
        print("=" * 60)
        print(str(e))
        print("\nPlease configure your AWS credentials in .env file")
        return False
    except Exception as e:
        print("=" * 60)
        print("❌ Error")
        print("=" * 60)
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_tables()
    sys.exit(0 if success else 1)

