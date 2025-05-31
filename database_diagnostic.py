#!/usr/bin/env python3
"""
Database Diagnostic Script
Checks user data and fixes missing test users
"""

import os
import sys
import duckdb
import bcrypt
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from db import get_db_connection

def check_user_data():
    """Check what test users exist and their data quality"""
    print("🔍 Checking Test User Data...")
    print("=" * 50)
    
    try:
        with get_db_connection() as conn:
            # Check users table
            users = conn.execute("""
                SELECT username, email, path, created_at 
                FROM users 
                WHERE username LIKE 'test%'
                ORDER BY username
            """).fetchall()
            
            print(f"📋 Found {len(users)} test users in users table:")
            for user in users:
                print(f"   {user[0]:15} | {user[1]:20} | {user[2]:20} | {user[3]}")
            
            print(f"\n📊 Checking sovereignty data for each user:")
            
            for user in users:
                username = user[0]
                
                # Check sovereignty data
                data_count = conn.execute("""
                    SELECT COUNT(*) FROM sovereignty WHERE username = ?
                """, [username]).fetchone()[0]
                
                if data_count > 0:
                    # Get data summary
                    summary = conn.execute("""
                        SELECT 
                            COUNT(*) as total_days,
                            AVG(score) as avg_score,
                            MIN(timestamp) as first_entry,
                            MAX(timestamp) as last_entry
                        FROM sovereignty 
                        WHERE username = ?
                    """, [username]).fetchone()
                    
                    print(f"   ✅ {username:15} | {data_count:3} days | Avg: {summary[1]:5.1f} | Range: {summary[2]} to {summary[3]}")
                else:
                    print(f"   ❌ {username:15} | No sovereignty data found")
            
            return users
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return []

def create_missing_test_users():
    """Create any missing test users"""
    print(f"\n🔧 Creating Missing Test Users...")
    print("=" * 50)
    
    required_users = [
        ("test", "dmh4681@gmail.com", "default"),
        ("test_physical", "dmh4681@gmail.com", "physical_optimization"),
        ("test_financial", "dmh4681@gmail.com", "financial_path"),
        ("test_mental", "dmh4681@gmail.com", "mental_resilience"),
        ("test_spiritual", "dmh4681@gmail.com", "spiritual_growth"),
        ("test_planetary", "dmh4681@gmail.com", "planetary_stewardship")
    ]
    
    try:
        with get_db_connection() as conn:
            # Check which users exist
            existing_users = set()
            try:
                users = conn.execute("SELECT username FROM users").fetchall()
                existing_users = {user[0] for user in users}
            except:
                print("   Creating users table...")
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        username    TEXT PRIMARY KEY,
                        email       TEXT NOT NULL,
                        password    TEXT NOT NULL,
                        path        TEXT NOT NULL,
                        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            
            # Create missing users
            password = "test123"
            salt = bcrypt.gensalt()
            hashed_pw = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
            
            for username, email, path in required_users:
                if username not in existing_users:
                    try:
                        conn.execute("""
                            INSERT INTO users (username, email, password, path) 
                            VALUES (?, ?, ?, ?)
                        """, (username, email, hashed_pw, path))
                        print(f"   ✅ Created: {username:15} | {path}")
                    except Exception as e:
                        print(f"   ❌ Failed to create {username}: {e}")
                else:
                    # Update email if needed
                    try:
                        conn.execute("""
                            UPDATE users 
                            SET email = ? 
                            WHERE username = ?
                        """, (email, username))
                        print(f"   🔄 Updated: {username:15} | Email set to {email}")
                    except Exception as e:
                        print(f"   ⚠️  {username}: {e}")
    
    except Exception as e:
        print(f"❌ Error creating users: {e}")

def check_data_intelligence_issue():
    """Specifically check what's causing the data intelligence failure"""
    print(f"\n🔍 Diagnosing Data Intelligence Issues...")
    print("=" * 50)
    
    try:
        # Import and test the problematic users
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Private"))
        from data_intelligence_agent import DataIntelligenceAgent
        
        agent = DataIntelligenceAgent()
        problem_users = ["test_mental", "test_spiritual"]
        
        for username in problem_users:
            print(f"   Testing {username}...")
            
            try:
                with get_db_connection() as conn:
                    # Check if user exists in users table
                    user_check = conn.execute("""
                        SELECT username, path FROM users WHERE username = ?
                    """, [username]).fetchone()
                    
                    if not user_check:
                        print(f"      ❌ User {username} not found in users table")
                        continue
                    
                    print(f"      ✅ User exists: {user_check[0]} | {user_check[1]}")
                    
                    # Check sovereignty data
                    data_check = conn.execute("""
                        SELECT COUNT(*) FROM sovereignty WHERE username = ?
                    """, [username]).fetchone()[0]
                    
                    print(f"      📊 Sovereignty entries: {data_check}")
                    
                    if data_check == 0:
                        print(f"      ⚠️  No sovereignty data - this will cause analysis to fail")
                    else:
                        # Try the analysis
                        result = agent.analyze_user(username)
                        if result and "error" not in result:
                            print(f"      ✅ Analysis successful")
                        else:
                            print(f"      ❌ Analysis failed: {result.get('error', 'Unknown error')}")
                            
            except Exception as e:
                print(f"      ❌ Error testing {username}: {e}")
    
    except Exception as e:
        print(f"❌ Error in diagnosis: {e}")

def main():
    """Run diagnostics and fixes"""
    print("🩺 SOVEREIGNTY DATABASE DIAGNOSTIC")
    print("=" * 60)
    
    # Check current state
    users = check_user_data()
    
    # Create missing users
    create_missing_test_users()
    
    # Diagnose data intelligence issues
    check_data_intelligence_issue()
    
    print(f"\n" + "=" * 60)
    print("🏁 Diagnostic Complete!")
    print("Run the email system test again to see if issues are resolved.")
    print("=" * 60)

if __name__ == "__main__":
    main()