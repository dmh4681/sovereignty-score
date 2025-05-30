#!/usr/bin/env python3
"""
Debug script to check users table and sovereignty data
"""

import os
import sys
import duckdb
from contextlib import contextmanager

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "data", "sovereignty.duckdb")

@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = duckdb.connect(DB_PATH)
        yield conn
    finally:
        if conn:
            conn.close()

def check_database_status():
    """Check the status of both users and sovereignty tables"""
    print("🔍 CHECKING DATABASE STATUS")
    print("=" * 50)
    
    try:
        with get_db_connection() as conn:
            # Check what tables exist
            tables = conn.execute("SHOW TABLES").fetchall()
            print(f"📋 Tables found: {[table[0] for table in tables]}")
            
            # Check users table
            if any('users' in str(table) for table in tables):
                try:
                    user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
                    print(f"👥 Users table: {user_count} users found")
                    
                    if user_count > 0:
                        users = conn.execute("SELECT username, email, path, created_at FROM users").fetchall()
                        print("📊 User details:")
                        for username, email, path, created_at in users:
                            print(f"   • {username} ({email}) - {path} - Created: {created_at}")
                    else:
                        print("⚠️  Users table is empty!")
                        
                except Exception as e:
                    print(f"❌ Error reading users table: {e}")
            else:
                print("❌ Users table not found!")
                
            # Check sovereignty table
            if any('sovereignty' in str(table) for table in tables):
                try:
                    data_count = conn.execute("SELECT COUNT(*) FROM sovereignty").fetchone()[0]
                    print(f"📈 Sovereignty table: {data_count} records found")
                    
                    if data_count > 0:
                        unique_users = conn.execute("SELECT DISTINCT username FROM sovereignty").fetchall()
                        print(f"📊 Users with data: {[user[0] for user in unique_users]}")
                    
                except Exception as e:
                    print(f"❌ Error reading sovereignty table: {e}")
            else:
                print("❌ Sovereignty table not found!")
                
            # Check table schemas
            print("\n📋 Table schemas:")
            for table_name in ['users', 'sovereignty']:
                try:
                    schema = conn.execute(f"DESCRIBE {table_name}").fetchall()
                    print(f"\n{table_name.upper()} TABLE:")
                    for col_name, col_type, nullable, key, default, extra in schema:
                        key_indicator = " (PK)" if key else ""
                        print(f"   {col_name:20s} {col_type:15s}{key_indicator}")
                except Exception as e:
                    print(f"   {table_name}: {e}")
                    
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False
        
    return True

def recreate_users_table():
    """Recreate the users table if needed"""
    print("\n🔧 RECREATING USERS TABLE")
    print("=" * 50)
    
    try:
        with get_db_connection() as conn:
            # Drop and recreate users table
            conn.execute("DROP TABLE IF EXISTS users")
            conn.execute("""
                CREATE TABLE users (
                    username    TEXT PRIMARY KEY,
                    email       TEXT NOT NULL,
                    password    TEXT NOT NULL,
                    path        TEXT NOT NULL,
                    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Users table recreated successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error recreating users table: {e}")
        return False

def create_test_user():
    """Create a test user for debugging"""
    print("\n👤 CREATING TEST USER")
    print("=" * 50)
    
    import bcrypt
    
    try:
        with get_db_connection() as conn:
            # Create test user
            username = "test"
            email = "test@example.com"
            password = "test123"
            path = "default"
            
            # Hash password
            salt = bcrypt.gensalt()
            hashed_pw = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
            
            # Insert user
            conn.execute("""
                INSERT INTO users (username, email, password, path) 
                VALUES (?, ?, ?, ?)
            """, (username, email, hashed_pw, path))
            
            print(f"✅ Test user created:")
            print(f"   Username: {username}")
            print(f"   Password: {password}")
            print(f"   Email: {email}")
            print(f"   Path: {path}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return False

def main():
    """Main debug function"""
    print("🛡️  SOVEREIGNTY SCORE USER DEBUG")
    print("=" * 60)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        return
    
    # Check current status
    if not check_database_status():
        return
    
    # Ask what to do
    print("\n" + "=" * 60)
    print("🔧 REPAIR OPTIONS:")
    print("1. Recreate users table and add test user")
    print("2. Just add a test user to existing table")
    print("3. Exit (just show status)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        if recreate_users_table():
            create_test_user()
    elif choice == "2":
        create_test_user()
    elif choice == "3":
        print("👋 Exiting without changes")
    else:
        print("❌ Invalid choice")
    
    print("\n" + "=" * 60)
    print("✅ Debug complete")
    print("=" * 60)

if __name__ == "__main__":
    main()