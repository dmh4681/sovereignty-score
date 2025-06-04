#!/usr/bin/env python3
"""
Enhanced data deletion script for Sovereignty Score database
Interactive user management with performance analysis
"""

import os
import sys
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection

def get_user_performance_summary(username):
    """Get detailed performance summary for a user"""
    try:
        with get_db_connection() as conn:
            # Basic stats
            stats = conn.execute("""
                SELECT 
                    COUNT(*) as total_days,
                    AVG(score) as avg_score,
                    MIN(score) as min_score,
                    MAX(score) as max_score,
                    MIN(timestamp) as first_entry,
                    MAX(timestamp) as last_entry,
                    ANY_VALUE(path) as path
                FROM sovereignty 
                WHERE username = ?
            """, [username]).fetchone()
            
            if not stats or stats[0] == 0:
                return None
            
            total_days, avg_score, min_score, max_score, first_entry, last_entry, path = stats
            
            # Recent performance (last 30 days)
            recent_stats = conn.execute("""
                SELECT AVG(score) as recent_avg
                FROM sovereignty 
                WHERE username = ? AND timestamp >= ?
            """, [username, datetime.now() - timedelta(days=30)]).fetchone()
            
            recent_avg = recent_stats[0] if recent_stats[0] else avg_score
            
            # Consistency metrics
            consistency_score = ((100 - (max_score - min_score)) / 100) * 100
            
            # Performance level determination
            if avg_score >= 80:
                performance_level = "🌟 Excellent"
            elif avg_score >= 60:
                performance_level = "👍 Good"
            elif avg_score >= 40:
                performance_level = "⚖️ Average"
            elif avg_score >= 20:
                performance_level = "📉 Poor"
            else:
                performance_level = "🆘 Struggling"
            
            # Trend analysis
            if recent_avg > avg_score + 5:
                trend = "📈 Improving"
            elif recent_avg < avg_score - 5:
                trend = "📉 Declining"
            else:
                trend = "➡️ Stable"
            
            return {
                'total_days': total_days,
                'avg_score': avg_score,
                'recent_avg': recent_avg,
                'min_score': min_score,
                'max_score': max_score,
                'consistency': consistency_score,
                'performance_level': performance_level,
                'trend': trend,
                'path': path,
                'first_entry': first_entry,
                'last_entry': last_entry,
                'date_range': f"{first_entry.strftime('%Y-%m-%d')} to {last_entry.strftime('%Y-%m-%d')}"
            }
            
    except Exception as e:
        print(f"❌ Error getting user summary: {e}")
        return None

def display_user_details(username, summary):
    """Display detailed user information"""
    print(f"\n📊 DETAILED ANALYSIS FOR {username.upper()}")
    print("=" * 50)
    print(f"🎯 Path: {summary['path'].replace('_', ' ').title()}")
    print(f"📅 Date Range: {summary['date_range']}")
    print(f"📈 Total Days: {summary['total_days']}")
    print(f"🏆 Average Score: {summary['avg_score']:.1f}/100")
    print(f"📊 Recent Average (30d): {summary['recent_avg']:.1f}/100")
    print(f"📉 Score Range: {summary['min_score']} - {summary['max_score']}")
    print(f"⚖️ Consistency: {summary['consistency']:.1f}%")
    print(f"🎭 Performance Level: {summary['performance_level']}")
    print(f"📈 Trend: {summary['trend']}")

def delete_user_data(username):
    """Delete all data for a specific user"""
    try:
        with get_db_connection() as conn:
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
            
            print(f"✅ Successfully deleted {count_before} records for user {username}")
            return True
            
    except Exception as e:
        print(f"❌ Error deleting user data: {e}")
        return False

def delete_all_data():
    """Delete all data from sovereignty table"""
    try:
        with get_db_connection() as conn:
            count_before = conn.execute("SELECT COUNT(*) FROM sovereignty").fetchone()[0]
            conn.execute("DELETE FROM sovereignty")
            
            print(f"✅ Successfully deleted all {count_before} records from database")
            return True
            
    except Exception as e:
        print(f"❌ Error deleting all data: {e}")
        return False

def list_all_users():
    """List all users with their basic stats"""
    try:
        with get_db_connection() as conn:
            users = conn.execute("""
                SELECT 
                    username, 
                    path,
                    COUNT(*) as record_count,
                    AVG(score) as avg_score,
                    MIN(timestamp) as first_entry,
                    MAX(timestamp) as last_entry
                FROM sovereignty 
                GROUP BY username, path
                ORDER BY avg_score DESC
            """).fetchall()
            
            if not users:
                print("📭 No users found in database")
                return []
            
            print("📊 CURRENT USERS IN DATABASE:")
            print("=" * 80)
            print(f"{'#':<3} {'Username':<15} {'Path':<18} {'Records':<8} {'Avg Score':<10} {'Performance':<12} {'Date Range':<20}")
            print("-" * 80)
            
            for i, (username, path, count, avg_score, first, last) in enumerate(users, 1):
                # Determine performance level
                if avg_score >= 80:
                    perf_indicator = "🌟 Excellent"
                elif avg_score >= 60:
                    perf_indicator = "👍 Good"
                elif avg_score >= 40:
                    perf_indicator = "⚖️ Average"
                elif avg_score >= 20:
                    perf_indicator = "📉 Poor"
                else:
                    perf_indicator = "🆘 Struggling"
                
                date_range = f"{first.strftime('%m/%d')} - {last.strftime('%m/%d')}"
                path_short = path.replace('_', ' ')[:16]
                
                print(f"{i:<3} {username:<15} {path_short:<18} {count:<8} {avg_score:<10.1f} {perf_indicator:<12} {date_range:<20}")
            
            print("-" * 80)
            print(f"Total: {len(users)} users")
            return users
            
    except Exception as e:
        print(f"❌ Error listing users: {e}")
        return []

def interactive_user_selection(users):
    """Interactive user selection menu"""
    while True:
        try:
            choice = input(f"\nSelect user (1-{len(users)}) or 'q' to quit: ").strip().lower()
            
            if choice == 'q':
                return None
            
            user_index = int(choice) - 1
            if 0 <= user_index < len(users):
                return users[user_index]
            else:
                print(f"❌ Please enter a number between 1 and {len(users)}")
                
        except ValueError:
            print("❌ Please enter a valid number or 'q' to quit")

def main():
    """Enhanced main function with detailed user management"""
    print("🗑️  SOVEREIGNTY SCORE DATA MANAGEMENT")
    print("=" * 60)
    
    while True:
        users = list_all_users()
        
        if not users:
            print("\n💡 No data to manage. Run TestData.py to generate test users.")
            break
        
        print(f"\n🔧 Management Options:")
        print("1. 📊 View detailed user analysis")
        print("2. 🗑️ Delete specific user's data")
        print("3. 💥 Delete ALL data (DANGER!)")
        print("4. 🔄 Refresh user list")
        print("5. 🚪 Exit")
        
        try:
            main_choice = input("\nSelect option (1-5): ").strip()
            
            if main_choice == "1":
                # View detailed user analysis
                print(f"\n📊 SELECT USER FOR DETAILED ANALYSIS:")
                selected_user = interactive_user_selection(users)
                
                if selected_user:
                    username = selected_user[0]
                    summary = get_user_performance_summary(username)
                    
                    if summary:
                        display_user_details(username, summary)
                        
                        # AI Coaching insights
                        print(f"\n🤖 AI COACHING INSIGHTS:")
                        if summary['avg_score'] >= 80:
                            print("   🎯 This user should trigger CELEBRATION and OPTIMIZATION coaching")
                            print("   💌 Expect emails about leveling up and advanced challenges")
                        elif summary['avg_score'] >= 60:
                            print("   📈 This user should trigger OPTIMIZATION coaching")
                            print("   💌 Expect emails about consistency improvements and next-level goals")
                        elif summary['avg_score'] >= 40:
                            print("   ⚖️ This user should trigger COURSE_CORRECTION coaching")
                            print("   💌 Expect emails about realignment and motivation")
                        elif summary['avg_score'] >= 20:
                            print("   🔄 This user should trigger INTERVENTION coaching")
                            print("   💌 Expect emails about support and rebuilding foundation")
                        else:
                            print("   🆘 This user should trigger urgent INTERVENTION coaching")
                            print("   💌 Expect emails about crisis support and small wins")
                        
                        input("\nPress Enter to continue...")
                    else:
                        print(f"❌ Could not load details for {username}")
                
            elif main_choice == "2":
                # Delete specific user
                print(f"\n🗑️ SELECT USER TO DELETE:")
                selected_user = interactive_user_selection(users)
                
                if selected_user:
                    username = selected_user[0]
                    summary = get_user_performance_summary(username)
                    
                    if summary:
                        display_user_details(username, summary)
                    
                    print(f"\n⚠️  WARNING: This will permanently delete ALL data for {username}")
                    confirm = input(f"Type '{username}' to confirm deletion: ").strip()
                    
                    if confirm == username:
                        if delete_user_data(username):
                            print(f"✅ User {username} deleted successfully!")
                            print("💡 You can now regenerate this user with different performance using TestData.py")
                        else:
                            print(f"❌ Failed to delete user {username}")
                    else:
                        print("❌ Deletion cancelled - username didn't match")
                
            elif main_choice == "3":
                # Delete all data
                print(f"\n💥 DELETE ALL DATA")
                print("⚠️  WARNING: This will permanently delete ALL sovereignty data for ALL users")
                print("   This action cannot be undone!")
                
                total_records = sum(user[2] for user in users)
                print(f"   Total records to delete: {total_records}")
                
                confirm1 = input("\nType 'DELETE ALL' to proceed: ").strip()
                if confirm1 == "DELETE ALL":
                    confirm2 = input("Are you absolutely sure? Type 'YES' to confirm: ").strip()
                    if confirm2 == "YES":
                        if delete_all_data():
                            print("✅ All data deleted successfully!")
                            print("💡 Database is now empty - ready for fresh test data")
                            break
                        else:
                            print("❌ Failed to delete all data")
                    else:
                        print("❌ Final confirmation failed - deletion cancelled")
                else:
                    print("❌ Deletion cancelled")
                
            elif main_choice == "4":
                # Refresh (just continue the loop)
                print("🔄 Refreshing user list...")
                continue
                
            elif main_choice == "5":
                # Exit
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid option. Please select 1-5.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()