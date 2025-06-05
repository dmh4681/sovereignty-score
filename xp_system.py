#!/usr/bin/env python3
"""
XP Transaction Engine - Sovereignty Score Gamification System
COMPLETE FIXED VERSION - Replace your existing xp_system.py with this
"""

import uuid
from datetime import datetime, date
import duckdb
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class XPTransactionEngine:
    """
    Manages XP transactions, challenges, and gamification for sovereignty tracking
    FIXED VERSION - No more constraint errors!
    """
    
    def __init__(self, db_path=None):
        if db_path is None:
            # Use the same path as your main app
            base_dir = os.path.dirname(__file__)
            if "Private" in base_dir:
                # If running from Private folder, go up to project root
                base_dir = os.path.dirname(base_dir)
            db_path = os.path.join(base_dir, "data", "sovereignty.duckdb")
        
        self.db_path = db_path
        logger.info(f"XP Engine using database: {db_path}")
        self._init_tables()
    
    def _init_tables(self):
        """Initialize XP system tables with proper constraints - FIXED VERSION"""
        try:
            with duckdb.connect(self.db_path) as conn:
                logger.info("Initializing XP system tables...")
                
                # Drop existing tables to fix constraint issues
                conn.execute("DROP TABLE IF EXISTS xp_transactions")
                conn.execute("DROP TABLE IF EXISTS daily_challenge_completion") 
                conn.execute("DROP TABLE IF EXISTS weekly_quest_progress")
                conn.execute("DROP TABLE IF EXISTS achievement_unlocks")
                
                # Create xp_transactions table with simple, working structure
                conn.execute("""
                    CREATE TABLE xp_transactions (
                        transaction_id VARCHAR PRIMARY KEY,
                        user_name VARCHAR NOT NULL,
                        xp_amount INTEGER NOT NULL,
                        source VARCHAR NOT NULL,
                        description TEXT,
                        reference_id VARCHAR,
                        multiplier REAL DEFAULT 1.0,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create daily_challenge_completion table with simple structure
                conn.execute("""
                    CREATE TABLE daily_challenge_completion (
                        completion_id VARCHAR PRIMARY KEY,
                        user_name VARCHAR NOT NULL,
                        challenge_id VARCHAR NOT NULL,
                        challenge_type VARCHAR NOT NULL,
                        xp_reward INTEGER NOT NULL,
                        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create weekly_quest_progress table
                conn.execute("""
                    CREATE TABLE weekly_quest_progress (
                        quest_id VARCHAR PRIMARY KEY,
                        user_name VARCHAR NOT NULL,
                        week_start DATE NOT NULL,
                        quest_type VARCHAR NOT NULL,
                        progress INTEGER DEFAULT 0,
                        target INTEGER NOT NULL,
                        completed BOOLEAN DEFAULT FALSE,
                        xp_reward INTEGER,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create achievement_unlocks table
                conn.execute("""
                    CREATE TABLE achievement_unlocks (
                        unlock_id VARCHAR PRIMARY KEY,
                        user_name VARCHAR NOT NULL,
                        achievement_id VARCHAR NOT NULL,
                        xp_reward INTEGER NOT NULL,
                        unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                logger.info("✅ XP system tables created successfully")
                
        except Exception as e:
            logger.error(f"❌ Error initializing XP tables: {e}")
            raise
    
    def award_xp(self, user_name, xp_amount, source, description="", reference_id=None, multiplier=1.0):
        """Award XP to a user with proper ID handling - FIXED VERSION"""
        try:
            # Generate unique transaction_id
            transaction_id = f"{user_name}_{source}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Generate unique reference_id if not provided
            if reference_id is None:
                reference_id = f"{source}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
            
            with duckdb.connect(self.db_path) as conn:
                # Check if this reference_id already exists (prevent duplicates)
                existing = conn.execute("""
                    SELECT COUNT(*) FROM xp_transactions 
                    WHERE user_name = ? AND reference_id = ?
                """, [user_name, reference_id]).fetchone()[0]
                
                if existing > 0:
                    logger.warning(f"⚠️ XP already awarded for reference_id: {reference_id}")
                    return False
                
                # Insert new XP transaction
                final_xp = int(xp_amount * multiplier)
                
                conn.execute("""
                    INSERT INTO xp_transactions 
                    (transaction_id, user_name, xp_amount, source, description, reference_id, multiplier, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    transaction_id,
                    user_name, 
                    final_xp, 
                    source, 
                    description, 
                    reference_id, 
                    multiplier, 
                    datetime.now()
                ])
                
                logger.info(f"✅ Awarded {final_xp} XP to {user_name} (source: {source})")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error awarding XP: {e}")
            return False
    
    def complete_daily_challenge(self, user_name, challenge_id, challenge_type, xp_reward):
        """Complete a daily challenge and award XP - FIXED VERSION"""
        try:
            # Generate unique completion_id
            completion_id = f"{user_name}_{challenge_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
            
            with duckdb.connect(self.db_path) as conn:
                # Check if challenge already completed today
                today = date.today()
                existing = conn.execute("""
                    SELECT COUNT(*) FROM daily_challenge_completion 
                    WHERE user_name = ? AND challenge_id = ? AND DATE(completed_at) = ?
                """, [user_name, challenge_id, today]).fetchone()[0]
                
                if existing > 0:
                    logger.warning(f"⚠️ Challenge already completed today: {challenge_id}")
                    return False
                
                # Record challenge completion
                conn.execute("""
                    INSERT INTO daily_challenge_completion 
                    (completion_id, user_name, challenge_id, challenge_type, xp_reward, completed_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, [completion_id, user_name, challenge_id, challenge_type, xp_reward, datetime.now()])
                
                # Award the XP
                success = self.award_xp(
                    user_name=user_name,
                    xp_amount=xp_reward,
                    source="daily_challenge",
                    description=f"Daily Challenge: {challenge_type}",
                    reference_id=f"challenge_{challenge_id}_{today.strftime('%Y%m%d')}"
                )
                
                if success:
                    logger.info(f"✅ Challenge completed: {challenge_id} (+{xp_reward} XP)")
                    return True
                else:
                    # Rollback challenge completion if XP award failed
                    conn.execute("""
                        DELETE FROM daily_challenge_completion 
                        WHERE completion_id = ?
                    """, [completion_id])
                    logger.warning(f"⚠️ Rolled back challenge completion due to XP award failure")
                    return False
                
        except Exception as e:
            logger.error(f"❌ Error completing challenge: {e}")
            return False
    
    def get_user_total_xp(self, user_name):
        """Get user's total XP and breakdown - FIXED VERSION"""
        try:
            with duckdb.connect(self.db_path) as conn:
                # Get total XP
                total_result = conn.execute("""
                    SELECT COALESCE(SUM(xp_amount), 0) as total_xp
                    FROM xp_transactions 
                    WHERE user_name = ?
                """, [user_name]).fetchone()
                
                total_xp = total_result[0] if total_result else 0
                
                # Get XP breakdown by source
                breakdown_result = conn.execute("""
                    SELECT source, SUM(xp_amount) as xp
                    FROM xp_transactions 
                    WHERE user_name = ?
                    GROUP BY source
                    ORDER BY xp DESC
                """, [user_name]).fetchall()
                
                breakdown = [{"source": row[0], "xp": row[1]} for row in breakdown_result]
                
                # Get recent transactions (last 10)
                recent_result = conn.execute("""
                    SELECT xp_amount, source, description, multiplier, timestamp
                    FROM xp_transactions 
                    WHERE user_name = ?
                    ORDER BY timestamp DESC
                    LIMIT 10
                """, [user_name]).fetchall()
                
                recent_transactions = [
                    {
                        "xp": row[0],
                        "source": row[1],
                        "description": row[2],
                        "multiplier": row[3],
                        "timestamp": row[4]
                    }
                    for row in recent_result
                ]
                
                return {
                    "total_xp": total_xp,
                    "breakdown": breakdown,
                    "recent_transactions": recent_transactions
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting user XP: {e}")
            return {"total_xp": 0, "breakdown": [], "recent_transactions": []}
    
    def get_daily_challenge_status(self, user_name, target_date=None):
        """Get challenge completion status for a specific date - FIXED VERSION"""
        if target_date is None:
            target_date = date.today()
        
        try:
            with duckdb.connect(self.db_path) as conn:
                # Get challenges completed on target date
                completed_result = conn.execute("""
                    SELECT challenge_id, challenge_type, xp_reward, completed_at
                    FROM daily_challenge_completion 
                    WHERE user_name = ? AND DATE(completed_at) = ?
                    ORDER BY completed_at DESC
                """, [user_name, target_date]).fetchall()
                
                completed_challenges = [
                    {
                        "challenge_id": row[0],
                        "challenge_type": row[1],
                        "xp_reward": row[2],
                        "completed_at": row[3],
                        "completed": True
                    }
                    for row in completed_result
                ]
                
                total_completed = len(completed_challenges)
                total_xp_earned = sum(c["xp_reward"] for c in completed_challenges)
                
                return {
                    "completed_challenges": completed_challenges,
                    "total_completed": total_completed,
                    "total_xp_earned": total_xp_earned
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting challenge status: {e}")
            return {"completed_challenges": [], "total_completed": 0, "total_xp_earned": 0}
    
    def get_xp_leaderboard(self, limit=10, timeframe="weekly"):
        """Get XP leaderboard for specified timeframe"""
        try:
            with duckdb.connect(self.db_path) as conn:
                # Calculate date filter based on timeframe
                if timeframe == "weekly":
                    date_filter = "WHERE timestamp >= CURRENT_DATE - INTERVAL 7 DAYS"
                elif timeframe == "monthly":
                    date_filter = "WHERE timestamp >= CURRENT_DATE - INTERVAL 30 DAYS"
                else:  # all_time
                    date_filter = ""
                
                query = f"""
                    SELECT 
                        user_name,
                        SUM(xp_amount) as total_xp,
                        (SUM(xp_amount) / 100) + 1 as level,
                        ROW_NUMBER() OVER (ORDER BY SUM(xp_amount) DESC) as rank
                    FROM xp_transactions 
                    {date_filter}
                    GROUP BY user_name
                    ORDER BY total_xp DESC
                    LIMIT ?
                """
                
                result = conn.execute(query, [limit]).fetchall()
                
                return [
                    {
                        "rank": row[3],
                        "user_name": row[0],
                        "total_xp": row[1],
                        "level": int(row[2])
                    }
                    for row in result
                ]
                
        except Exception as e:
            logger.error(f"❌ Error getting leaderboard: {e}")
            return []
    
    def reset_daily_challenges(self, user_name, target_date=None):
        """Reset daily challenges for testing purposes"""
        if target_date is None:
            target_date = date.today()
        
        try:
            with duckdb.connect(self.db_path) as conn:
                # Delete challenge completions for the target date
                conn.execute("""
                    DELETE FROM daily_challenge_completion 
                    WHERE user_name = ? AND DATE(completed_at) = ?
                """, [user_name, target_date])
                
                # Delete related XP transactions
                conn.execute("""
                    DELETE FROM xp_transactions 
                    WHERE user_name = ? AND source = 'daily_challenge' AND DATE(timestamp) = ?
                """, [user_name, target_date])
                
                logger.info(f"✅ Reset daily challenges for {user_name} on {target_date}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error resetting challenges: {e}")
            return False

# Helper functions for dashboard integration
def get_gamification_data_real(xp_engine, user_name):
    """Get real gamification data from XP system - FIXED VERSION"""
    
    # Get XP data
    xp_data = xp_engine.get_user_total_xp(user_name)
    total_xp = xp_data["total_xp"]
    
    # Calculate level (100 XP per level)
    current_level = (total_xp // 100) + 1
    xp_in_current_level = total_xp % 100
    xp_to_next_level = 100 - xp_in_current_level
    
    # Get today's XP
    today = date.today()
    today_challenge_status = xp_engine.get_daily_challenge_status(user_name, today)
    today_xp = today_challenge_status["total_xp_earned"]
    
    return {
        "total_xp": total_xp,
        "current_level": current_level,
        "xp_in_current_level": xp_in_current_level,
        "xp_to_next_level": xp_to_next_level,
        "today_xp": today_xp,
        "breakdown": xp_data["breakdown"],
        "recent_transactions": xp_data["recent_transactions"]
    }

def handle_challenge_completion(xp_engine, user_name, challenge_data):
    """Handle challenge completion - FIXED VERSION"""
    return xp_engine.complete_daily_challenge(
        user_name=user_name,
        challenge_id=challenge_data["challenge_id"],
        challenge_type=challenge_data["challenge_type"],
        xp_reward=challenge_data["xp_reward"]
    )

def get_event_multiplier():
    """Get current event multiplier based on season/date"""
    current_month = datetime.now().month
    
    # Seasonal multipliers
    if current_month in [12, 1, 2]:  # Winter
        return {"bitcoin": 2.0, "default": 1.0, "season": "Winter Bitcoin Accumulation"}
    elif current_month in [6, 7, 8]:  # Summer  
        return {"exercise": 2.0, "default": 1.0, "season": "Summer Fitness Boost"}
    elif current_month in [11]:  # November
        return {"gratitude": 3.0, "default": 1.0, "season": "Gratitude Season"}
    else:
        return {"default": 1.0, "season": "Standard"}

def main():
    """Test the XP system"""
    print("🎮 TESTING XP TRANSACTION ENGINE")
    print("=" * 50)
    
    # Initialize engine
    engine = XPTransactionEngine()
    
    # Test user
    test_user = "test_user"
    
    # Test awarding XP
    print("\n1. Testing XP Awards...")
    success1 = engine.award_xp(test_user, 25, "test", "Test XP award #1")
    success2 = engine.award_xp(test_user, 50, "achievement", "Test achievement unlock", "ach_001")
    
    print(f"Award 1 success: {success1}")
    print(f"Award 2 success: {success2}")
    
    # Test challenge completion
    print("\n2. Testing Challenge Completion...")
    success3 = engine.complete_daily_challenge(test_user, "meditation_test", "meditation", 30)
    print(f"Challenge completion success: {success3}")
    
    # Test duplicate prevention
    print("\n3. Testing Duplicate Prevention...")
    success4 = engine.complete_daily_challenge(test_user, "meditation_test", "meditation", 30)
    print(f"Duplicate challenge success (should be False): {success4}")
    
    # Get user XP data
    print("\n4. Testing XP Retrieval...")
    xp_data = engine.get_user_total_xp(test_user)
    print(f"Total XP: {xp_data['total_xp']}")
    print(f"XP Breakdown: {xp_data['breakdown']}")
    
    # Test challenge status
    print("\n5. Testing Challenge Status...")
    status = engine.get_daily_challenge_status(test_user)
    print(f"Challenges completed today: {status['total_completed']}")
    print(f"XP earned today: {status['total_xp_earned']}")
    
    # Test gamification data
    print("\n6. Testing Gamification Integration...")
    gamification = get_gamification_data_real(engine, test_user)
    print(f"Level: {gamification['current_level']}")
    print(f"Today's XP: {gamification['today_xp']}")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()