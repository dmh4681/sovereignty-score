#!/usr/bin/env python3
"""
Enhanced debug script for managing users table
Can see passwords, change emails, and bulk restore users
"""

import os
import sys
import bcrypt
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection, init_db

def check_database_status():
    """Check current database status"""
    print("🔍 CHECKING DATABASE STATUS")
    print("=" * 50)
    
    try:
        with get_db_connection() as conn:
            # Check tables
            tables = conn.execute("SHOW TABLES").fetchall()
            table_names = [table[0] for table in tables]
            print(f"📋 Tables found: {table_names}")
            
            # Check users table
            if 'users' in table_names:
                user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
                print(f"👥 Users table: {user_count} users found")
                
                if user_count > 0:
                    users = conn.execute("SELECT username, email, path FROM users").fetchall()
                    print("   Current users:")
                    for username, email, path in users:
                        print(f"      • {username} ({email}) - {path}")
                else:
                    print("⚠️  Users table is empty!")
            
            # Check sovereignty table
            if 'sovereignty' in table_names:
                sov_count = conn.execute("SELECT COUNT(*) FROM sovereignty").fetchone()[0]
                print(f"📈 Sovereignty table: {sov_count} records found")
                
                if sov_count > 0:
                    sov_users = conn.execute("""
                        SELECT DISTINCT username, path, COUNT(*) as records, MIN(timestamp) as first_entry
                        FROM sovereignty 
                        GROUP BY username, path 
                        ORDER BY first_entry
                    """).fetchall()
                    print("📊 Users with sovereignty data:")
                    for username, path, records, first_entry in sov_users:
                        date_str = first_entry.strftime('%Y-%m-%d') if first_entry else 'Unknown'
                        print(f"      • {username} ({path}) - {records} records since {date_str}")
                    
                    return sov_users
            
            return []
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return []

def show_user_passwords():
    """Show existing users and their password hashes (for debugging)"""
    try:
        with get_db_connection() as conn:
            users = conn.execute("SELECT username, email, password, path, created_at FROM users").fetchall()
            
            if not users:
                print("📭 No users found in users table")
                return
            
            print("\n🔑 CURRENT USER CREDENTIALS")
            print("=" * 60)
            for username, email, password_hash, path, created_at in users:
                print(f"Username: {username}")
                print(f"Email: {email}")
                print(f"Path: {path}")
                print(f"Created: {created_at}")
                print(f"Password Hash: {password_hash[:20]}... (bcrypt)")
                print(f"Test Login: http://localhost:8501/?username={username}&path={path}")
                print("-" * 40)
                
    except Exception as e:
        print(f"❌ Error showing passwords: {e}")

def test_password(username, test_password="test123"):
    """Test if a password works for a user"""
    try:
        with get_db_connection() as conn:
            user = conn.execute("SELECT password FROM users WHERE username = ?", [username]).fetchone()
            if not user:
                print(f"❌ User {username} not found")
                return False
            
            stored_hash = user[0]
            if bcrypt.checkpw(test_password.encode('utf-8'), stored_hash.encode('utf-8')):
                print(f"✅ Password '{test_password}' works for {username}")
                return True
            else:
                print(f"❌ Password '{test_password}' doesn't work for {username}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing password: {e}")
        return False

def change_user_email(username, new_email):
    """Change email for a specific user"""
    try:
        with get_db_connection() as conn:
            # Check if user exists
            user = conn.execute("SELECT username FROM users WHERE username = ?", [username]).fetchone()
            if not user:
                print(f"❌ User {username} not found")
                return False
            
            # Update email
            conn.execute("UPDATE users SET email = ? WHERE username = ?", [new_email, username])
            print(f"✅ Updated {username} email to {new_email}")
            return True
            
    except Exception as e:
        print(f"❌ Error updating email: {e}")
        return False

def change_user_password(username, new_password):
    """Change password for a specific user"""
    try:
        with get_db_connection() as conn:
            # Check if user exists
            user = conn.execute("SELECT username FROM users WHERE username = ?", [username]).fetchone()
            if not user:
                print(f"❌ User {username} not found")
                return False
            
            # Hash new password
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
            
            # Update password
            conn.execute("UPDATE users SET password = ? WHERE username = ?", [hashed_password, username])
            print(f"✅ Updated {username} password")
            return True
            
    except Exception as e:
        print(f"❌ Error updating password: {e}")
        return False

def bulk_restore_users_from_sovereignty(target_email="dmh4681@gmail.com", target_password="test123"):
    """Restore all users from sovereignty data with your email and password"""
    try:
        with get_db_connection() as conn:
            # Get users from sovereignty data
            sov_users = conn.execute("""
                SELECT DISTINCT username, path, MIN(timestamp) as first_entry
                FROM sovereignty 
                GROUP BY username, path 
                ORDER BY first_entry
            """).fetchall()
            
            if not sov_users:
                print("❌ No sovereignty data found")
                return False
            
            print(f"🔧 BULK RESTORE: {len(sov_users)} users with email {target_email}")
            print("=" * 60)
            
            # Hash the target password once
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(target_password.encode('utf-8'), salt).decode('utf-8')
            
            # Check existing users
            existing_users = conn.execute("SELECT username FROM users").fetchall()
            existing_usernames = {user[0] for user in existing_users}
            
            added_count = 0
            updated_count = 0
            
            for username, path, first_entry in sov_users:
                if username in existing_usernames:
                    # Update existing user
                    conn.execute("""
                        UPDATE users 
                        SET email = ?, password = ?, path = ? 
                        WHERE username = ?
                    """, [target_email, hashed_password, path, username])
                    print(f"🔄 Updated: {username} ({path})")
                    updated_count += 1
                else:
                    # Add new user
                    conn.execute("""
                        INSERT INTO users (username, email, password, path, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, [username, target_email, hashed_password, path, first_entry or datetime.now()])
                    print(f"➕ Added: {username} ({path})")
                    added_count += 1
            
            print(f"\n✅ Bulk restore complete!")
            print(f"   Added: {added_count} new users")
            print(f"   Updated: {updated_count} existing users")
            print(f"   All users now have:")
            print(f"      Email: {target_email}")
            print(f"      Password: {target_password}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during bulk restore: {e}")
        return False

def main():
    """Enhanced main function"""
    print("🛡️  SOVEREIGNTY SCORE USER DEBUG")
    print("=" * 60)
    
    # Initialize database
    init_db()
    
    # Check current status
    sovereignty_users = check_database_status()
    
    print("\n🔧 MANAGEMENT OPTIONS:")
    print("1. 👀 Show current user passwords/credentials")
    print("2. 🧪 Test password for a user")
    print("3. 📧 Change email for a specific user")
    print("4. 🔑 Change password for a specific user")
    print("5. 🚀 BULK RESTORE: Add/update ALL sovereignty users with your email")
    print("6. ➕ Add single new user manually")
    print("7. 🔄 Refresh status")
    print("8. 🚪 Exit")
    
    while True:
        try:
            choice = input(f"\nSelect option (1-8): ").strip()
            
            if choice == "1":
                show_user_passwords()
                
            elif choice == "2":
                username = input("Username to test: ").strip()
                password = input("Password to test (default: test123): ").strip() or "test123"
                test_password(username, password)
                
            elif choice == "3":
                username = input("Username: ").strip()
                email = input("New email (default: dmh4681@gmail.com): ").strip() or "dmh4681@gmail.com"
                change_user_email(username, email)
                
            elif choice == "4":
                username = input("Username: ").strip()
                password = input("New password (default: test123): ").strip() or "test123"
                change_user_password(username, password)
                
            elif choice == "5":
                print(f"\n🚀 BULK RESTORE ALL SOVEREIGNTY USERS")
                print("This will add/update ALL users from sovereignty data")
                email = input("Email for all users (default: dmh4681@gmail.com): ").strip() or "dmh4681@gmail.com"
                password = input("Password for all users (default: test123): ").strip() or "test123"
                
                print(f"\n⚠️  This will set ALL users to:")
                print(f"   Email: {email}")
                print(f"   Password: {password}")
                
                if sovereignty_users:
                    print(f"   Users to add/update: {len(sovereignty_users)}")
                    for username, path, records, first_entry in sovereignty_users:
                        print(f"      • {username} ({path})")
                
                confirm = input("\nProceed? (y/N): ").strip().lower()
                if confirm == 'y':
                    if bulk_restore_users_from_sovereignty(email, password):
                        print("\n🎉 All users restored! You can now log in with:")
                        print(f"   Email: {email}")
                        print(f"   Password: {password}")
                        print(f"   Any username from your sovereignty data")
                else:
                    print("❌ Cancelled")
                
            elif choice == "6":
                print("\n➕ ADD NEW USER MANUALLY")
                username = input("Username: ").strip()
                email = input("Email (default: dmh4681@gmail.com): ").strip() or "dmh4681@gmail.com"
                password = input("Password (default: test123): ").strip() or "test123"
                
                paths = ['default', 'financial_path', 'mental_resilience', 'physical_optimization', 'spiritual_growth', 'planetary_stewardship']
                print("Available paths:")
                for i, path in enumerate(paths, 1):
                    print(f"   {i}. {path}")
                
                try:
                    path_choice = int(input(f"Select path (1-{len(paths)}): ")) - 1
                    path = paths[path_choice]
                except (ValueError, IndexError):
                    path = 'default'
                
                # Add user
                try:
                    with get_db_connection() as conn:
                        salt = bcrypt.gensalt()
                        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
                        
                        conn.execute("""
                            INSERT INTO users (username, email, password, path, created_at)
                            VALUES (?, ?, ?, ?, ?)
                        """, [username, email, hashed_password, path, datetime.now()])
                        
                        print(f"✅ Added user {username} successfully!")
                        
                except Exception as e:
                    print(f"❌ Error adding user: {e}")
                
            elif choice == "7":
                sovereignty_users = check_database_status()
                
            elif choice == "8":
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid option. Please select 1-8.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()