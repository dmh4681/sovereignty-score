#!/usr/bin/env python3
"""
Delete test data from Sovereignty Score database
Updated for new database structure
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection

def delete_user_data(username=None):
    """Delete data for specific user or all data"""
    try:
        with get_db_connection() as conn:
            if username:
                # Delete specific user
                count_before = conn.execute(
                    "SELECT COUNT(*) FROM sovereignty WHERE username = ?", [username]
                ).fetchone()[0]
                
                if count_before == 0:
                    print(f"❌ No data found for user: {username}")
                    return False
                
                conn.execute("DELETE FROM sovereignty WHERE username = ?", [username])
                
                count_after = conn.execute(
                    "SELECT COUNT(*) FROM sovereignty WHERE username = ?", [username]
                ).fetchone()[0]
                
                print(f"✅ Deleted {count_before} records for user {username}")
                print(f"   Remaining records for {username}: {count_after}")
            else:
                # Delete all data
                count_before = conn.execute("SELECT COUNT(*) FROM sovereignty").fetchone()[0]
                conn.execute("DELETE FROM sovereignty")
                count_after = conn.execute("SELECT COUNT(*) FROM sovereignty").fetchone()[0]
                
                print(f"✅ Deleted {count_before} total records")
                print(f"   Remaining records: {count_after}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error deleting data: {e}")
        return False

def main():
    """Main deletion function with user interaction"""
    print("🗑️  SOVEREIGNTY SCORE DATA DELETION")
    print("=" * 50)
    
    try:
        with get_db_connection() as conn:
            # Show current users
            users = conn.execute(
                "SELECT username, COUNT(*) as record_count FROM sovereignty GROUP BY username"
            ).fetchall()
            
            if not users:
                print("📭 No data found in database")
                return
            
            print("📊 Current users and their data:")
            for username, count in users:
                print(f"   • {username}: {count} records")
            
            print("\n🔧 Deletion options:")
            print("1. Delete specific user's data")
            print("2. Delete ALL data")
            print("3. Cancel")
            
            choice = input("\nEnter choice (1-3): ").strip()
            
            if choice == "1":
                print("\nAvailable users:")
                for i, (username, count) in enumerate(users, 1):
                    print(f"   {i}. {username} ({count} records)")
                
                try:
                    user_choice = int(input(f"\nSelect user (1-{len(users)}): ")) - 1
                    if 0 <= user_choice < len(users):
                        selected_user = users[user_choice][0]
                        confirm = input(f"Delete all data for {selected_user}? (y/N): ").strip().lower()
                        if confirm == 'y':
                            delete_user_data(selected_user)
                        else:
                            print("❌ Cancelled")
                    else:
                        print("❌ Invalid selection")
                except (ValueError, IndexError):
                    print("❌ Invalid input")
                    
            elif choice == "2":
                confirm = input("⚠️  Delete ALL sovereignty data? This cannot be undone! (y/N): ").strip().lower()
                if confirm == 'y':
                    delete_user_data()
                else:
                    print("❌ Cancelled")
                    
            elif choice == "3":
                print("👋 Cancelled")
            else:
                print("❌ Invalid choice")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()