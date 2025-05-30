#!/usr/bin/env python3
"""
Database migration and cleanup script for Sovereignty Score
Fixes field order issues and validates data integrity
"""

import os
import sys
import duckdb
import json
from datetime import datetime
import shutil
from contextlib import contextmanager

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backup_db import create_backup

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "data", "sovereignty.duckdb")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")

@contextmanager
def get_db_connection():
    """Get database connection with error handling"""
    conn = None
    try:
        conn = duckdb.connect(DB_PATH)
        yield conn
    finally:
        if conn:
            conn.close()

def analyze_database_issues():
    """Analyze the current database for potential issues"""
    print("🔍 Analyzing database for issues...")
    
    try:
        with get_db_connection() as conn:
            # Check if database exists and has data
            try:
                row_count = conn.execute("SELECT COUNT(*) FROM sovereignty").fetchone()[0]
                print(f"📊 Found {row_count} records in sovereignty table")
            except Exception as e:
                print(f"❌ Error accessing sovereignty table: {e}")
                return False
            
            if row_count == 0:
                print("✅ Database is empty - no migration needed")
                return True
            
            # Check for data inconsistencies
            sample_data = conn.execute("""
                SELECT timestamp, username, path, btc_usd, btc_sats, score,
                       home_cooked_meals, exercise_minutes
                FROM sovereignty 
                ORDER BY timestamp DESC 
                LIMIT 5
            """).fetchall()
            
            print("\n📋 Sample records:")
            print("Timestamp | User | Path | BTC_USD | BTC_Sats | Score | Meals | Exercise")
            print("-" * 80)
            
            suspicious_records = 0
            for record in sample_data:
                timestamp, username, path, btc_usd, btc_sats, score, meals, exercise = record
                
                # Check for suspicious values
                is_suspicious = False
                issues = []
                
                if btc_usd and btc_usd < 0:
                    issues.append("negative BTC")
                    is_suspicious = True
                if score and (score < 0 or score > 100):
                    issues.append(f"invalid score ({score})")
                    is_suspicious = True
                if meals and meals > 10:
                    issues.append(f"excessive meals ({meals})")
                    is_suspicious = True
                if exercise and exercise > 500:
                    issues.append(f"excessive exercise ({exercise})")
                    is_suspicious = True
                
                if is_suspicious:
                    suspicious_records += 1
                    status = f"⚠️  {', '.join(issues)}"
                else:
                    status = "✅"
                
                print(f"{str(timestamp)[:19]} | {username[:8]:8s} | {path[:8]:8s} | "
                      f"{btc_usd:7.2f} | {btc_sats:8d} | {score:3d} | {meals:5d} | "
                      f"{exercise:8d} | {status}")
            
            if suspicious_records > 0:
                print(f"\n⚠️  Found {suspicious_records} potentially corrupted records")
                return False
            else:
                print("\n✅ No obvious data corruption detected")
                return True
                
    except Exception as e:
        print(f"❌ Error analyzing database: {e}")
        return False

def create_migration_backup():
    """Create a backup before migration"""
    print("💾 Creating backup before migration...")
    
    try:
        # Ensure backup directory exists
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        # Create timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"pre_migration_{timestamp}.duckdb"
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        
        shutil.copy2(DB_PATH, backup_path)
        print(f"✅ Backup created: {backup_name}")
        return backup_path
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def migrate_database():
    """Migrate database to fix field order issues"""
    print("🔧 Starting database migration...")
    
    try:
        with get_db_connection() as conn:
            # Create new table with correct schema
            conn.execute("""
                CREATE TABLE sovereignty_new (
                    timestamp            TIMESTAMP,
                    username             VARCHAR,
                    path                 VARCHAR,
                    home_cooked_meals    INTEGER,
                    junk_food            BOOLEAN,
                    exercise_minutes     INTEGER,
                    strength_training    BOOLEAN,
                    no_spending          BOOLEAN,
                    invested_bitcoin     BOOLEAN,
                    btc_usd              REAL DEFAULT 0,
                    btc_sats             INTEGER DEFAULT 0,
                    meditation           BOOLEAN,
                    gratitude            BOOLEAN,
                    read_or_learned      BOOLEAN,
                    environmental_action BOOLEAN,
                    score                INTEGER
                )
            """)
            
            # Copy data with explicit column mapping
            conn.execute("""
                INSERT INTO sovereignty_new (
                    timestamp, username, path,
                    home_cooked_meals, junk_food, exercise_minutes, strength_training,
                    no_spending, invested_bitcoin, btc_usd, btc_sats,
                    meditation, gratitude, read_or_learned, environmental_action, score
                )
                SELECT 
                    timestamp, username, path,
                    home_cooked_meals, junk_food, exercise_minutes, strength_training,
                    no_spending, invested_bitcoin, btc_usd, btc_sats,
                    meditation, gratitude, read_or_learned, environmental_action, score
                FROM sovereignty
                WHERE score >= 0 AND score <= 100  -- Filter out invalid scores
                AND home_cooked_meals >= 0 AND home_cooked_meals <= 10  -- Reasonable meal count
                AND exercise_minutes >= 0 AND exercise_minutes <= 500   -- Reasonable exercise
            """)
            
            # Get counts
            old_count = conn.execute("SELECT COUNT(*) FROM sovereignty").fetchone()[0]
            new_count = conn.execute("SELECT COUNT(*) FROM sovereignty_new").fetchone()[0]
            
            print(f"📊 Migrated {new_count} of {old_count} records")
            
            if new_count < old_count:
                filtered_count = old_count - new_count
                print(f"⚠️  Filtered out {filtered_count} invalid records")
            
            # Replace old table with new one
            conn.execute("DROP TABLE sovereignty")
            conn.execute("ALTER TABLE sovereignty_new RENAME TO sovereignty")
            
            print("✅ Database migration completed successfully")
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def validate_migrated_data():
    """Validate the migrated database"""
    print("🔍 Validating migrated data...")
    
    try:
        with get_db_connection() as conn:
            # Check basic counts
            total_records = conn.execute("SELECT COUNT(*) FROM sovereignty").fetchone()[0]
            unique_users = conn.execute("SELECT COUNT(DISTINCT username) FROM sovereignty").fetchone()[0]
            
            print(f"📊 Total records: {total_records}")
            print(f"👥 Unique users: {unique_users}")
            
            # Check for data integrity
            integrity_checks = [
                ("Valid scores", "SELECT COUNT(*) FROM sovereignty WHERE score >= 0 AND score <= 100"),
                ("Valid meals", "SELECT COUNT(*) FROM sovereignty WHERE home_cooked_meals >= 0 AND home_cooked_meals <= 10"),
                ("Valid exercise", "SELECT COUNT(*) FROM sovereignty WHERE exercise_minutes >= 0 AND exercise_minutes <= 500"),
                ("Valid BTC amounts", "SELECT COUNT(*) FROM sovereignty WHERE btc_usd >= 0")
            ]
            
            all_valid = True
            for check_name, query in integrity_checks:
                valid_count = conn.execute(query).fetchone()[0]
                if valid_count == total_records:
                    print(f"✅ {check_name}: {valid_count}/{total_records}")
                else:
                    print(f"❌ {check_name}: {valid_count}/{total_records}")
                    all_valid = False
            
            if all_valid:
                print("✅ All data validation checks passed")
            else:
                print("⚠️  Some data validation issues remain")
            
            return all_valid
            
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

def main():
    """Main migration function"""
    print("🛡️  SOVEREIGNTY SCORE DATABASE MIGRATION")
    print("=" * 50)
    
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print("❌ Database not found. Please ensure the database exists.")
        return False
    
    # Step 1: Analyze current issues
    if not analyze_database_issues():
        print("\n⚠️  Issues detected. Proceeding with migration...")
    else:
        print("\n✅ Database appears healthy. Migration may not be necessary.")
        response = input("Continue with migration anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("Migration cancelled.")
            return True
    
    # Step 2: Create backup
    backup_path = create_migration_backup()
    if not backup_path:
        print("❌ Cannot proceed without backup. Migration cancelled.")
        return False
    
    # Step 3: Perform migration
    if not migrate_database():
        print("❌ Migration failed. Database backup preserved.")
        return False
    
    # Step 4: Validate results
    if not validate_migrated_data():
        print("⚠️  Migration completed but validation issues remain.")
    
    print("\n" + "=" * 50)
    print("✅ DATABASE MIGRATION COMPLETED")
    print(f"💾 Backup saved: {os.path.basename(backup_path)}")
    print("🔧 Database schema and data integrity improved")
    print("🚀 Ready to use the updated Sovereignty Score app")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate Sovereignty Score database")
    parser.add_argument("--analyze-only", action="store_true",
                       help="Only analyze database, don't migrate")
    parser.add_argument("--force", action="store_true",
                       help="Force migration even if database appears healthy")
    
    args = parser.parse_args()
    
    if args.analyze_only:
        analyze_database_issues()
    else:
        success = main()
        if not success:
            sys.exit(1)