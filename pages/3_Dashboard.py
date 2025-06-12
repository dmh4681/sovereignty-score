import streamlit as st

st.set_page_config(
    page_title="Sovereignty Dashboard",
    page_icon="🏆",
    layout="wide"
)
st.session_state['use_simple_xp'] = True  # Force simple XP system

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import sys
import os
import uuid

# Add project root and Private folder to path
project_root = os.path.dirname(os.path.dirname(__file__))
private_path = os.path.join(project_root, "Private")

# Add both paths
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if private_path not in sys.path:
    sys.path.insert(0, private_path)

from db import get_db_connection
from sovereignty_achievements import SovereigntyAchievementEngine

# NEW: Import the real XP system
from xp_system import XPTransactionEngine, get_gamification_data_real, handle_challenge_completion

# REMOVED: AQAL imports
# try:
#     from sovereignty_achievements import IntegratedSovereigntyEngine
#     AQAL_AVAILABLE = True
# except ImportError:
#     AQAL_AVAILABLE = False
AQAL_AVAILABLE = False  # Disabled

# Enhanced CSS for gamified sovereignty styling
st.markdown("""
<style>
    .gamification-hub {
        background: linear-gradient(135deg, #1f2937, #374151);
        border: 3px solid #6366f1;
        border-radius: 16px;
        padding: 20px;
        margin: 12px 0;
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.3);
    }
    
    .xp-card {
        background: linear-gradient(45deg, #059669, #10b981);
        color: white;
        padding: 16px;
        border-radius: 12px;
        text-align: center;
        margin: 6px 0;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
    
    .level-card {
        background: linear-gradient(45deg, #7c3aed, #a78bfa);
        color: white;
        padding: 16px;
        border-radius: 12px;
        text-align: center;
        margin: 6px 0;
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);
    }
    
    .streak-card {
        background: linear-gradient(45deg, #ef4444, #f97316);
        color: white;
        padding: 12px;
        border-radius: 12px;
        text-align: center;
        margin: 6px 0;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
        transition: transform 0.2s;
    }
    
    .streak-card:hover {
        transform: scale(1.05);
    }
    
    .achievement-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        margin: 4px;
        font-weight: bold;
        text-align: center;
        transition: transform 0.2s;
        cursor: pointer;
        font-size: 13px;
    }
    
    .achievement-badge:hover {
        transform: scale(1.05);
    }
    
    .legendary { 
        background: linear-gradient(45deg, #f59e0b, #fbbf24); 
        color: #1f2937;
        border: 2px solid #d97706;
    }
    .epic { 
        background: linear-gradient(45deg, #7c3aed, #a78bfa); 
        color: white;
        border: 2px solid #5b21b6;
    }
    .rare { 
        background: linear-gradient(45deg, #3b82f6, #60a5fa); 
        color: white;
        border: 2px solid #1d4ed8;
    }
    .common { 
        background: linear-gradient(45deg, #6b7280, #9ca3af); 
        color: white;
        border: 2px solid #4b5563;
    }
    
    .sovereignty-metric {
        text-align: center;
        padding: 12px;
        background: rgba(99, 102, 241, 0.1);
        border-radius: 12px;
        border: 2px solid rgba(99, 102, 241, 0.3);
        margin: 6px 0;
        transition: transform 0.2s;
    }
    
    .sovereignty-metric:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
    }
    
    .compact-achievement {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(99, 102, 241, 0.05));
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 8px;
        padding: 10px;
        margin: 4px 0;
        font-size: 13px;
    }
    
    .next-achievement-compact {
        background: linear-gradient(135deg, #059669, #10b981);
        color: white;
        padding: 10px;
        border-radius: 8px;
        margin: 6px 0;
        font-size: 13px;
    }
    
    .financial-gamification {
        background: linear-gradient(135deg, #f59e0b, #fbbf24);
        color: #1f2937;
        padding: 12px;
        border-radius: 12px;
        margin: 8px 0;
        font-weight: bold;
        font-size: 14px;
    }
    
    .xp-progress-bar {
        background: rgba(255,255,255,0.3);
        border-radius: 10px;
        height: 10px;
        margin: 6px 0;
        overflow: hidden;
    }
    
    .xp-progress-fill {
        background: linear-gradient(45deg, #ffffff, #e5e7eb);
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    /* Compact styles for condensed dashboard */
    .compact-metric {
        padding: 8px !important;
        margin: 4px 0 !important;
    }
    
    .compact-header {
        margin: 8px 0 !important;
        font-size: 18px !important;
    }
</style>
""", unsafe_allow_html=True)

# Get user info from query params or session state
username = st.query_params.get("username", None) or st.session_state.get("username", None)
path = st.query_params.get("path", None) or st.session_state.get("path", None)

# Store in session state if we got it from query params
if st.query_params.get("username"):
    st.session_state.username = st.query_params.get("username")
if st.query_params.get("path"):
    st.session_state.path = st.query_params.get("path")

if not username or not path:
    st.error("🚨 Please log in through the main page to access your dashboard.")
    st.stop()

# Header with sovereignty branding (more compact)
st.markdown(f"""
<div style="text-align: center; padding: 12px 0;">
    <h1 style="color: #6366f1; margin: 0;">🛡️ Sovereignty Dashboard</h1>
    <p style="color: #9ca3af; margin: 4px 0;">Welcome back, <strong>{username}</strong> • Path: <strong>{path.replace('_', ' ').title()}</strong></p>
</div>
""", unsafe_allow_html=True)

# Initialize XP system
@st.cache_resource
def init_xp_engine():
    """Initialize and cache the XP engine"""
    return XPTransactionEngine()

# Initialize achievement engine
@st.cache_data(ttl=300)
def get_user_achievements(username):
    """Get user achievements with caching"""
    engine = SovereigntyAchievementEngine()
    return engine.calculate_user_achievements(username)

# Simple XP calculation functions
def calculate_gamification_metrics_real(username, achievements_data):
    """Calculate XP using ONLY the simple, reliable system"""
    return get_simple_gamification_data(username)

def render_xp_display_enhanced_safe(gamification_data):
    """Enhanced XP display with better error handling"""
    
    # Extract basic data with safe defaults
    total_xp = gamification_data.get("total_xp", 0)
    current_level = gamification_data.get("current_level", 1)
    xp_progress = gamification_data.get("xp_in_current_level", 0)
    today_xp = gamification_data.get("today_xp", 0)
    
    # Compact XP display
    st.markdown('<div class="gamification-hub">', unsafe_allow_html=True)
    
    # Header with real-time XP
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"### 🎮 Level {current_level} Sovereign")
        st.markdown(f"**{total_xp:,} Total XP**")
    
    with col2:
        if today_xp > 0:
            st.markdown(f"""
            <div class="xp-card" style="padding: 8px;">
                <h4 style="margin: 0;">⚡ +{today_xp}</h4>
                <small>Today</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        # Progress to next level (compact)
        st.markdown(f"""
        <div style="text-align: center;">
            <div class="xp-progress-bar">
                <div class="xp-progress-fill" style="width: {xp_progress}%;"></div>
            </div>
            <small style="color: #9ca3af;">{xp_progress}/100 to Lvl {current_level + 1}</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Helper Functions - Insert these where the comment was

def nuclear_reset_xp_system():
    """Nuclear reset - completely destroys and recreates XP tables"""
    import duckdb
    import os
    
    # Get database path
    base_dir = os.path.dirname(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, "data", "sovereignty.duckdb")
    
    try:
        with duckdb.connect(db_path) as conn:
            print("🔥 NUCLEAR RESET: Destroying all XP tables...")
            
            # Nuclear option: Drop everything XP-related
            tables_to_nuke = [
                "xp_transactions",
                "daily_challenge_completion", 
                "weekly_quest_progress",
                "achievement_unlocks",
                "xp_system",  # In case there are variations
                "gamification",
                "challenges"
            ]
            
            for table in tables_to_nuke:
                try:
                    conn.execute(f"DROP TABLE IF EXISTS {table}")
                    print(f"💥 Nuked table: {table}")
                except:
                    pass  # Table might not exist
            
            print("🏗️ Creating new XP tables with correct structure...")
            
            # Create XP transactions table (SIMPLE VERSION)
            conn.execute("""
                CREATE TABLE xp_transactions (
                    txn_id VARCHAR PRIMARY KEY,
                    user_name VARCHAR NOT NULL,
                    xp_points INTEGER NOT NULL,
                    xp_source VARCHAR NOT NULL,
                    xp_description TEXT,
                    xp_reference VARCHAR,
                    xp_multiplier REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create challenge completion table (SIMPLE VERSION)
            conn.execute("""
                CREATE TABLE daily_challenge_completion (
                    comp_id VARCHAR PRIMARY KEY,
                    user_name VARCHAR NOT NULL,
                    challenge_ref VARCHAR NOT NULL,
                    challenge_category VARCHAR NOT NULL,
                    points_earned INTEGER NOT NULL,
                    completion_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            print("✅ New XP tables created successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Nuclear reset failed: {e}")
        return False

class SimpleXPEngine:
    """Ultra-simple XP engine that actually works"""
    
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        self.db_path = os.path.join(base_dir, "data", "sovereignty.duckdb")
    
    def award_xp(self, username, xp_amount, source, description="", reference_id=None):
        """Award XP with simple structure"""
        try:
            import uuid
            from datetime import datetime
            import duckdb
            
            # Generate simple unique ID
            txn_id = f"{username}_{source}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"
            
            if reference_id is None:
                reference_id = f"{source}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            with duckdb.connect(self.db_path) as conn:
                # Check for duplicates
                existing = conn.execute("""
                    SELECT COUNT(*) FROM xp_transactions 
                    WHERE user_name = ? AND xp_reference = ?
                """, [username, reference_id]).fetchone()[0]
                
                if existing > 0:
                    print(f"⚠️ XP already awarded for: {reference_id}")
                    return False
                
                # Insert XP
                conn.execute("""
                    INSERT INTO xp_transactions 
                    (txn_id, user_name, xp_points, xp_source, xp_description, xp_reference)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, [txn_id, username, int(xp_amount), source, description, reference_id])
                
                print(f"✅ Awarded {xp_amount} XP to {username}")
                return True
                
        except Exception as e:
            print(f"❌ Error awarding XP: {e}")
            return False
    
    def complete_challenge(self, username, challenge_id, challenge_type, xp_reward):
        """Complete challenge with simple structure"""
        try:
            import uuid
            from datetime import datetime, date
            import duckdb
            
            comp_id = f"{username}_{challenge_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:4]}"
            
            with duckdb.connect(self.db_path) as conn:
                # Check if already completed today
                today = date.today()
                existing = conn.execute("""
                    SELECT COUNT(*) FROM daily_challenge_completion 
                    WHERE user_name = ? AND challenge_ref = ? AND DATE(completion_time) = ?
                """, [username, challenge_id, today]).fetchone()[0]
                
                if existing > 0:
                    print(f"⚠️ Challenge already completed: {challenge_id}")
                    return False
                
                # Record completion
                conn.execute("""
                    INSERT INTO daily_challenge_completion 
                    (comp_id, user_name, challenge_ref, challenge_category, points_earned)
                    VALUES (?, ?, ?, ?, ?)
                """, [comp_id, username, challenge_id, challenge_type, xp_reward])
                
                # Award XP
                success = self.award_xp(
                    username=username,
                    xp_amount=xp_reward,
                    source="daily_challenge",
                    description=f"Challenge: {challenge_type}",
                    reference_id=f"challenge_{challenge_id}_{today.strftime('%Y%m%d')}"
                )
                
                if success:
                    print(f"✅ Challenge completed: {challenge_id} (+{xp_reward} XP)")
                    return True
                else:
                    # Rollback
                    conn.execute("DELETE FROM daily_challenge_completion WHERE comp_id = ?", [comp_id])
                    return False
                
        except Exception as e:
            print(f"❌ Error completing challenge: {e}")
            return False
    
    def get_user_xp(self, username):
        """Get user XP data"""
        try:
            import duckdb
            
            with duckdb.connect(self.db_path) as conn:
                # Total XP
                total_result = conn.execute("""
                    SELECT COALESCE(SUM(xp_points), 0) 
                    FROM xp_transactions 
                    WHERE user_name = ?
                """, [username]).fetchone()
                
                total_xp = total_result[0] if total_result else 0
                
                # Recent transactions
                recent_result = conn.execute("""
                    SELECT xp_points, xp_source, xp_description, created_at
                    FROM xp_transactions 
                    WHERE user_name = ?
                    ORDER BY created_at DESC
                    LIMIT 5
                """, [username]).fetchall()
                
                recent = [
                    {
                        "xp": row[0],
                        "source": row[1], 
                        "description": row[2],
                        "timestamp": row[3]
                    }
                    for row in recent_result
                ]
                
                return {
                    "total_xp": total_xp,
                    "recent_transactions": recent
                }
                
        except Exception as e:
            print(f"❌ Error getting XP: {e}")
            return {"total_xp": 0, "recent_transactions": []}
    
    def get_today_challenges(self, username):
        """Get today's completed challenges"""
        try:
            import duckdb
            from datetime import date
            
            with duckdb.connect(self.db_path) as conn:
                today = date.today()
                
                result = conn.execute("""
                    SELECT challenge_ref, challenge_category, points_earned, completion_time
                    FROM daily_challenge_completion 
                    WHERE user_name = ? AND DATE(completion_time) = ?
                """, [username, today]).fetchall()
                
                completed = [
                    {
                        "challenge_id": row[0],
                        "challenge_type": row[1],
                        "xp_reward": row[2],
                        "completed_at": row[3],
                        "completed": True
                    }
                    for row in result
                ]
                
                return {
                    "completed_challenges": completed,
                    "total_completed": len(completed),
                    "total_xp_earned": sum(c["xp_reward"] for c in completed)
                }
                
        except Exception as e:
            print(f"❌ Error getting challenges: {e}")
            return {"completed_challenges": [], "total_completed": 0, "total_xp_earned": 0}

def get_simple_gamification_data(username):
    """Get gamification data using simple XP engine"""
    simple_engine = SimpleXPEngine()
    xp_data = simple_engine.get_user_xp(username)
    
    total_xp = xp_data["total_xp"]
    current_level = (total_xp // 100) + 1
    xp_in_current_level = total_xp % 100
    
    # Get today's XP
    today_data = simple_engine.get_today_challenges(username)
    today_xp = today_data["total_xp_earned"]
    
    return {
        "total_xp": total_xp,
        "current_level": current_level,
        "xp_in_current_level": xp_in_current_level,
        "xp_to_next_level": 100 - xp_in_current_level,
        "today_xp": today_xp,
        "breakdown": [{"source": "simple", "xp": total_xp}],
        "recent_transactions": xp_data["recent_transactions"]
    }

def render_simple_challenges(username, path, current_streaks):
    """Render challenges with simple XP system"""
    
    simple_engine = SimpleXPEngine()
    
    # Generate challenges
    try:
        daily_challenges = generate_daily_challenges(username, path, current_streaks)
    except:
        # Fallback challenges
        daily_challenges = [
            {"type": "meditation", "description": "🧘‍♂️ Meditate today", "xp": 25, "icon": "🧘‍♂️"},
            {"type": "cooking", "description": "🍳 Cook a meal", "xp": 20, "icon": "🍳"},
            {"type": "exercise", "description": "💪 Exercise today", "xp": 30, "icon": "💪"}
        ]
    
    # Get completed challenges
    challenge_status = simple_engine.get_today_challenges(username)
    completed_ids = {c["challenge_id"] for c in challenge_status["completed_challenges"]}
    
    from datetime import date
    today_str = date.today().strftime("%Y%m%d")
    
    challenge_cols = st.columns(3)
    
    for i, challenge in enumerate(daily_challenges):
        with challenge_cols[i]:
            challenge_id = f"{today_str}_{challenge['type']}_{i}"
            is_completed = challenge_id in completed_ids
            
            if is_completed:
                st.markdown(f"""
                <div style="background: linear-gradient(45deg, #10b981, #059669); 
                            color: white; padding: 12px; border-radius: 8px;">
                    <div style="text-align: center;">
                        <h3 style="margin: 0;">{challenge['icon']}</h3>
                        <p style="margin: 4px 0; font-weight: bold;">✅ COMPLETED!</p>
                        <p style="margin: 0; font-size: 12px;">{challenge['description']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                if st.button(f"Complete", key=f"simple_{challenge_id}", use_container_width=True):
                    success = simple_engine.complete_challenge(
                        username, challenge_id, challenge['type'], challenge['xp']
                    )
                    if success:
                        st.success(f"🎉 +{challenge['xp']} XP!")
                        st.rerun()
                    else:
                        st.error("❌ Error or already completed")
                
                st.markdown(f"""
                <div style="background: rgba(99, 102, 241, 0.1); border-radius: 8px; padding: 12px; text-align: center;">
                    <h3 style="margin: 0; color: #6366f1;">{challenge['icon']}</h3>
                    <p style="margin: 4px 0; font-weight: bold;">{challenge['xp']} XP</p>
                    <p style="margin: 0; font-size: 12px;">{challenge['description']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    if challenge_status["total_completed"] > 0:
        st.success(f"🏆 {challenge_status['total_completed']}/3 completed (+{challenge_status['total_xp_earned']} XP)")

@st.cache_data(ttl=86400)  # Cache for 24 hours
def generate_weekly_quest(username, path, week_start):
    """Generate a weekly quest based on user's path"""
    
    weekly_quests = {
        "financial_path": [
            {"name": "💰 The Minimalist", "description": "Spend $0 on discretionary items for 5 days", "target": 5, "xp": 100, "type": "no_spending_days"},
            {"name": "₿ The Accumulator", "description": "Stack sats 4 times this week", "target": 4, "xp": 120, "type": "bitcoin_days"},
            {"name": "🍳 The Saver", "description": "Cook 15+ meals to maximize savings", "target": 15, "xp": 80, "type": "meals_cooked"},
            {"name": "📚 The Student", "description": "Learn about finance/investing 5 days", "target": 5, "xp": 90, "type": "learning_days"}
        ],
        "physical_optimization": [
            {"name": "💪 The Beast", "description": "Strength train 4+ times this week", "target": 4, "xp": 120, "type": "strength_days"},
            {"name": "🍳 The Chef", "description": "Cook 20+ high-protein meals", "target": 20, "xp": 100, "type": "meals_cooked"},
            {"name": "🏃 The Athlete", "description": "Exercise 6 days with 30+ minutes each", "target": 6, "xp": 110, "type": "exercise_days"},
            {"name": "🚫 The Disciplined", "description": "Zero junk food for entire week", "target": 7, "xp": 90, "type": "clean_eating_days"}
        ],
        "mental_resilience": [
            {"name": "🧘‍♂️ The Monk", "description": "Meditate every single day", "target": 7, "xp": 120, "type": "meditation_days"},
            {"name": "📚 The Scholar", "description": "Learn something new 6 days", "target": 6, "xp": 100, "type": "learning_days"},
            {"name": "🙏 The Grateful", "description": "Practice gratitude daily", "target": 7, "xp": 80, "type": "gratitude_days"},
            {"name": "⚡ The Focused", "description": "Achieve 80+ score 4 times", "target": 4, "xp": 110, "type": "high_score_days"}
        ],
        "spiritual_growth": [
            {"name": "🌅 The Mindful", "description": "Meditate and practice gratitude daily", "target": 7, "xp": 130, "type": "mindful_days"},
            {"name": "🌍 The Steward", "description": "Environmental action 5 days", "target": 5, "xp": 100, "type": "environmental_days"},
            {"name": "📝 The Reflective", "description": "Deep reflection/journaling 4 days", "target": 4, "xp": 90, "type": "reflection_days"},
            {"name": "🍽️ The Conscious", "description": "Mindful eating all week", "target": 7, "xp": 80, "type": "mindful_eating_days"}
        ],
        "planetary_stewardship": [
            {"name": "🌍 The Guardian", "description": "Environmental action every day", "target": 7, "xp": 130, "type": "environmental_days"},
            {"name": "♻️ The Zero-Waster", "description": "Minimal waste 6 days", "target": 6, "xp": 110, "type": "zero_waste_days"},
            {"name": "🥬 The Locavore", "description": "Local/organic food choices daily", "target": 7, "xp": 100, "type": "local_food_days"},
            {"name": "🚲 The Green Commuter", "description": "Walk/bike 5 times instead of driving", "target": 5, "xp": 90, "type": "green_transport_days"}
        ],
        "default": [
            {"name": "🎯 The Balanced", "description": "Score 70+ points for 5 days", "target": 5, "xp": 120, "type": "balanced_days"},
            {"name": "🔥 The Consistent", "description": "Track everything 7 days straight", "target": 7, "xp": 100, "type": "tracking_days"},
            {"name": "⭐ The Achiever", "description": "Complete 20+ daily activities", "target": 20, "xp": 90, "type": "activity_count"},
            {"name": "🚀 The Improver", "description": "Beat your average score 4 times", "target": 4, "xp": 110, "type": "improvement_days"}
        ]
    }
    
    available_quests = weekly_quests.get(path, weekly_quests["default"])
    import random
    return random.choice(available_quests)

@st.cache_data(ttl=300)
def generate_daily_challenges(username, path, current_streaks):
    """Generate 3 daily challenges based on user's path and current progress"""
    
    # Challenge pool by path
    path_challenges = {
        "financial_path": [
            {"type": "no_spending", "description": "💰 No discretionary spending today", "xp": 25, "icon": "💰"},
            {"type": "bitcoin_investment", "description": "₿ Stack some sats today", "xp": 30, "icon": "₿"},
            {"type": "read_learn", "description": "📚 Learn something about money/investing", "xp": 20, "icon": "📚"},
            {"type": "meal_prep", "description": "🍳 Cook 2+ meals to save money", "xp": 25, "icon": "🍳"},
            {"type": "budget_review", "description": "📊 Track your expenses", "xp": 15, "icon": "📊"}
        ],
        "physical_optimization": [
            {"type": "strength_training", "description": "💪 Complete strength training", "xp": 30, "icon": "💪"},
            {"type": "protein_focus", "description": "🥩 Hit your protein target", "xp": 20, "icon": "🥩"},
            {"type": "meal_prep", "description": "🍳 Cook 3+ high-protein meals", "xp": 25, "icon": "🍳"},
            {"type": "no_junk", "description": "🚫 Zero junk food today", "xp": 20, "icon": "🚫"},
            {"type": "exercise_plus", "description": "🏃 30+ minutes of exercise", "xp": 25, "icon": "🏃"}
        ],
        "mental_resilience": [
            {"type": "meditation", "description": "🧘‍♂️ Complete meditation session", "xp": 25, "icon": "🧘‍♂️"},
            {"type": "gratitude", "description": "🙏 Practice gratitude", "xp": 15, "icon": "🙏"},
            {"type": "read_learn", "description": "📖 Read for 30+ minutes", "xp": 20, "icon": "📖"},
            {"type": "digital_detox", "description": "📱 Limit screen time", "xp": 25, "icon": "📱"},
            {"type": "nature_time", "description": "🌿 Spend time in nature", "xp": 20, "icon": "🌿"}
        ],
        "spiritual_growth": [
            {"type": "meditation", "description": "🧘‍♂️ Deep meditation practice", "xp": 30, "icon": "🧘‍♂️"},
            {"type": "gratitude", "description": "🙏 Heartfelt gratitude practice", "xp": 20, "icon": "🙏"},
            {"type": "environmental", "description": "🌍 Take environmental action", "xp": 25, "icon": "🌍"},
            {"type": "mindful_eating", "description": "🍽️ Eat mindfully without distractions", "xp": 20, "icon": "🍽️"},
            {"type": "reflection", "description": "📝 Journal or reflect deeply", "xp": 25, "icon": "📝"}
        ],
        "planetary_stewardship": [
            {"type": "environmental", "description": "🌍 Take environmental action", "xp": 30, "icon": "🌍"},
            {"type": "zero_waste", "description": "♻️ Produce minimal waste", "xp": 25, "icon": "♻️"},
            {"type": "local_food", "description": "🥬 Choose local/organic food", "xp": 20, "icon": "🥬"},
            {"type": "walk_bike", "description": "🚲 Walk/bike instead of driving", "xp": 20, "icon": "🚲"},
            {"type": "conservation", "description": "💧 Practice resource conservation", "xp": 15, "icon": "💧"}
        ],
        "default": [
            {"type": "balanced_day", "description": "⚖️ Hit 70+ sovereignty score", "xp": 30, "icon": "⚖️"},
            {"type": "triple_threat", "description": "🎯 Cook, exercise, and meditate", "xp": 35, "icon": "🎯"},
            {"type": "consistency", "description": "📈 Log all activities", "xp": 20, "icon": "📈"},
            {"type": "streak_building", "description": "🔥 Extend your longest streak", "xp": 25, "icon": "🔥"},
            {"type": "new_habit", "description": "✨ Try something new", "xp": 15, "icon": "✨"}
        ]
    }
    
    # Get challenges for this path
    available_challenges = path_challenges.get(path, path_challenges["default"])
    
    # Smart challenge selection based on weak areas
    weak_streaks = [k for k, v in current_streaks.items() if v < 3]
    priority_challenges = []
    
    # Add challenges that target weak areas
    for challenge in available_challenges:
        if any(weak in challenge["type"] for weak in weak_streaks):
            priority_challenges.append(challenge)
    
    # Fill remaining slots with random challenges
    import random
    remaining_challenges = [c for c in available_challenges if c not in priority_challenges]
    selected_challenges = priority_challenges[:2] + random.sample(remaining_challenges, min(2, len(remaining_challenges)))
    
    # Ensure we have exactly 3 challenges
    while len(selected_challenges) < 3:
        selected_challenges.append(random.choice(available_challenges))
    
    return selected_challenges[:3]

@st.cache_data(ttl=86400)  # Cache for 24 hours
def get_seasonal_event(current_date):
    """Generate seasonal sovereignty events based on time of year"""
    
    import datetime
    month = current_date.month
    day = current_date.day
    
    # Define seasonal events throughout the year
    seasonal_events = {
        "winter_accumulation": {
            "name": "❄️ Bitcoin Winter Accumulation",
            "period": "December 21 - March 20", 
            "theme": "Stack sats while others panic",
            "description": "When the markets are cold, true sovereigns accumulate. Double XP for Bitcoin investments during crypto winter.",
            "bonus": "2x XP for Bitcoin stacking",
            "color": "#3b82f6",
            "active_months": [12, 1, 2, 3],
            "challenges": [
                "Stack sats 5 days this week",
                "Read 3 Bitcoin articles", 
                "No FOMO buying - only DCA",
                "Calculate your stack growth"
            ]
        },
        "spring_renewal": {
            "name": "🌱 Spring Sovereignty Renewal", 
            "period": "March 21 - June 20",
            "theme": "Grow your body and mind",
            "description": "As nature awakens, so does your sovereignty. Focus on health, learning, and fresh habits.",
            "bonus": "2x XP for new habit streaks",
            "color": "#10b981", 
            "active_months": [3, 4, 5, 6],
            "challenges": [
                "Start 2 new healthy habits",
                "Cook with fresh spring ingredients",
                "Meditate outdoors daily",
                "Learn a new skill"
            ]
        },
        "summer_abundance": {
            "name": "☀️ Summer Abundance Festival",
            "period": "June 21 - September 20", 
            "theme": "Peak performance and energy",
            "description": "Harness summer's energy for maximum sovereignty gains. Focus on peak physical and mental performance.",
            "bonus": "2x XP for exercise and strength training",
            "color": "#f59e0b",
            "active_months": [6, 7, 8, 9],
            "challenges": [
                "Hit the gym 5x this week",
                "Meal prep like a champion", 
                "Morning sun exposure daily",
                "Achieve 3 personal records"
            ]
        },
        "autumn_harvest": {
            "name": "🍂 Autumn Sovereignty Harvest",
            "period": "September 21 - December 20",
            "theme": "Reap what you've sown", 
            "description": "Time to harvest the sovereignty you've built all year. Reflection, gratitude, and preparation.",
            "bonus": "2x XP for gratitude and reflection",
            "color": "#ea580c",
            "active_months": [9, 10, 11, 12],
            "challenges": [
                "Daily gratitude practice",
                "Review your year's progress",
                "Prepare for winter abundance",
                "Share sovereignty wisdom"
            ]
        }
    }
    
    # Special limited-time events
    special_events = {
        "new_year_sovereign": {
            "name": "🎆 New Year Sovereignty Revolution",
            "period": "January 1-31",
            "active_dates": [(1, 1, 31)],  # month, start_day, end_day
            "theme": "Start the year sovereign",
            "description": "New year, new sovereignty. 31 days to build the foundation for your most sovereign year yet.",
            "bonus": "Triple XP for starting new streaks",
            "color": "#8b5cf6"
        },
        "bitcoin_birthday": {
            "name": "₿ Bitcoin Birthday Celebration", 
            "period": "January 3-9",
            "active_dates": [(1, 3, 9)],
            "theme": "Genesis block anniversary",
            "description": "Celebrating the birth of sound money. Stack sats in honor of Satoshi's gift to humanity.",
            "bonus": "3x XP for Bitcoin activities",
            "color": "#f59e0b"
        },
        "summer_solstice": {
            "name": "🌞 Peak Sovereignty Solstice",
            "period": "June 21-27", 
            "active_dates": [(6, 21, 27)],
            "theme": "Longest day, strongest sovereign",
            "description": "Harness the year's peak energy for your sovereignty journey. Seven days of maximum effort.",
            "bonus": "2x XP for all activities",
            "color": "#fbbf24"
        },
        "thanksgiving_gratitude": {
            "name": "🦃 Sovereignty Gratitude Week",
            "period": "November 20-26",
            "active_dates": [(11, 20, 26)],
            "theme": "Grateful for freedom earned",
            "description": "A week to reflect on the sovereignty you've built and express gratitude for your journey.",
            "bonus": "3x XP for gratitude practice",
            "color": "#ea580c"
        }
    }
    
    # Check for special events first
    for event_id, event in special_events.items():
        for start_month, start_day, end_day in event.get("active_dates", []):
            if month == start_month and start_day <= day <= end_day:
                return {"type": "special", "id": event_id, **event}
    
    # Check for seasonal events
    for event_id, event in seasonal_events.items():
        if month in event["active_months"]:
            return {"type": "seasonal", "id": event_id, **event}
    
    return None

@st.cache_data(ttl=86400)
def get_seasonal_challenges(event_data):
    """Get today's seasonal challenges based on active event"""
    if not event_data:
        return []
    
    base_challenges = event_data.get("challenges", [])
    
    # Add event-specific bonus challenges
    if event_data["id"] == "winter_accumulation":
        bonus_challenges = [
            "Read about Bitcoin cold storage",
            "Calculate your DCA strategy", 
            "Ignore crypto news FUD"
        ]
    elif event_data["id"] == "spring_renewal":
        bonus_challenges = [
            "Try a new superfood",
            "Meditate in nature",
            "Start a learning project"
        ]
    elif event_data["id"] == "summer_abundance": 
        bonus_challenges = [
            "Morning workout in the sun",
            "Grill healthy proteins",
            "Take a cold shower"
        ]
    elif event_data["id"] == "autumn_harvest":
        bonus_challenges = [
            "Journal about growth this year",
            "Practice deep gratitude",
            "Prep for upcoming challenges"
        ]
    else:
        bonus_challenges = []
    
    # Combine and return up to 3 challenges
    all_challenges = base_challenges + bonus_challenges
    import random
    return random.sample(all_challenges, min(3, len(all_challenges)))

# Load user achievements
with st.spinner("🔍 Analyzing your sovereignty journey..."):
    achievements_data = get_user_achievements(username)

if "error" in achievements_data:
    st.error(f"❌ Error loading achievements: {achievements_data['error']}")
    st.stop()

# Use simple XP calculation
try:
    gamification_data = calculate_gamification_metrics_real(username, achievements_data)
except Exception as e:
    st.error(f"❌ XP System Error: {e}")
    gamification_data = get_simple_gamification_data(username)

# Extract achievement data
sovereignty_level = achievements_data.get("sovereignty_level", {})
earned_achievements = achievements_data.get("achievements_earned", [])
progress_metrics = achievements_data.get("progress_metrics", {})
next_achievements = achievements_data.get("next_achievements", [])
achievement_summary = achievements_data.get("achievement_summary", {})

# ═══════════════════════════════════════════════════════════════════
# MAIN DASHBOARD - CONDENSED LAYOUT
# ═══════════════════════════════════════════════════════════════════

# Row 1: XP Display + Sovereignty Level
render_xp_display_enhanced_safe(gamification_data)

# Row 2: Daily Challenges & Weekly Quest
st.markdown("---")
current_streaks = progress_metrics.get("current_streaks", {})
from datetime import datetime, timedelta
today = datetime.now()
week_start = today - timedelta(days=today.weekday())
weekly_quest = generate_weekly_quest(username, path, week_start.strftime("%Y-%m-%d"))

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("### ⚡ Daily Challenges")
    render_simple_challenges(username, path, current_streaks)

with col2:
    st.markdown("### 🏆 Weekly Quest")
    quest_progress = 2  # Mock data
    quest_target = weekly_quest["target"]
    quest_progress_pct = min(100, (quest_progress / quest_target) * 100)
    
    st.markdown(f"**{weekly_quest['name']}**")
    st.markdown(f"<small>{weekly_quest['description']}</small>", unsafe_allow_html=True)
    st.markdown(f"**Reward: {weekly_quest['xp']} XP**")
    
    # Progress bar
    st.markdown(f"""
    <div class="xp-progress-bar" style="margin: 8px 0;">
        <div class="xp-progress-fill" style="width: {quest_progress_pct}%;"></div>
    </div>
    <small>{quest_progress}/{quest_target} ({quest_progress_pct:.0f}%)</small>
    """, unsafe_allow_html=True)

# Row 3: Sovereignty Metrics + Active Streaks
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📊 Sovereignty Metrics")
    
    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
    
    with metrics_col1:
        sats = progress_metrics.get("total_sats_accumulated", 0)
        sats_progress = min(100, (sats / 100000000) * 100)
        st.markdown(f"""
        <div class="sovereignty-metric compact-metric">
            <h4 style="margin: 0; color: #f59e0b;">₿ {sats:,}</h4>
            <small>Sats • {sats_progress:.1f}% to 1 BTC</small>
        </div>
        """, unsafe_allow_html=True)
    
    with metrics_col2:
        meals = progress_metrics.get("total_meals_cooked", 0)
        meal_savings = meals * 12
        st.markdown(f"""
        <div class="sovereignty-metric compact-metric">
            <h4 style="margin: 0; color: #10b981;">🍳 {meals}</h4>
            <small>Meals • ${meal_savings:,} saved</small>
        </div>
        """, unsafe_allow_html=True)
    
    with metrics_col3:
        btc_invested = progress_metrics.get("total_btc_invested", 0)
        st.markdown(f"""
        <div class="sovereignty-metric compact-metric">
            <h4 style="margin: 0; color: #3b82f6;">${btc_invested:,.0f}</h4>
            <small>BTC Invested</small>
        </div>
        """, unsafe_allow_html=True)
    
    with metrics_col4:
        tracking_days = progress_metrics.get("total_tracking_days", 0)
        st.markdown(f"""
        <div class="sovereignty-metric compact-metric">
            <h4 style="margin: 0; color: #8b5cf6;">📅 {tracking_days}</h4>
            <small>Days Tracked</small>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("### 🔥 Active Streaks")
    
    current_streaks = progress_metrics.get("current_streaks", {})
    active_streaks = {k: v for k, v in current_streaks.items() if v > 0}
    
    if active_streaks:
        # Show top streaks in a compact grid
        top_streaks = sorted(active_streaks.items(), key=lambda x: x[1], reverse=True)[:4]
        streak_cols = st.columns(2)
        
        for i, (activity, days) in enumerate(top_streaks):
            col_idx = i % 2
            with streak_cols[col_idx]:
                activity_emoji = {
                    "meditation": "🧘‍♂️",
                    "gratitude": "🙏",
                    "strength_training": "💪",
                    "invested_bitcoin": "₿",
                    "environmental_action": "🌍",
                    "cooking": "👨‍🍳"
                }
                emoji = activity_emoji.get(activity, "⚡")
                
                st.markdown(f"""
                <div class="streak-card" style="padding: 8px;">
                    <strong>{emoji} {days} Days</strong>
                    <br><small>{activity.replace('_', ' ').title()}</small>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("💡 Start a new streak today!")

# ═══════════════════════════════════════════════════════════════════
# 📊 ACTIVITY COMPLETION RATES (Insert after Sovereignty Metrics)
# ═══════════════════════════════════════════════════════════════════

# Load activity data for completion rates
try:
    with get_db_connection() as conn:
        activity_data = conn.execute("""
            SELECT 
                AVG(CASE WHEN meditation THEN 1 ELSE 0 END) * 100 as meditation_rate,
                AVG(CASE WHEN gratitude THEN 1 ELSE 0 END) * 100 as gratitude_rate,
                AVG(CASE WHEN strength_training THEN 1 ELSE 0 END) * 100 as strength_rate,
                AVG(CASE WHEN no_spending THEN 1 ELSE 0 END) * 100 as no_spending_rate,
                AVG(CASE WHEN invested_bitcoin THEN 1 ELSE 0 END) * 100 as bitcoin_rate,
                AVG(CASE WHEN read_or_learned THEN 1 ELSE 0 END) * 100 as learning_rate,
                AVG(CASE WHEN environmental_action THEN 1 ELSE 0 END) * 100 as environmental_rate,
                AVG(CASE WHEN NOT junk_food THEN 1 ELSE 0 END) * 100 as no_junk_rate,
                AVG(home_cooked_meals) as avg_meals,
                AVG(exercise_minutes) as avg_exercise,
                AVG(btc_sats) as avg_sats
            FROM sovereignty 
            WHERE username = ?
        """, [username]).fetchone()
        
        if activity_data:
            st.markdown("### 📊 Activity Completion Rates")
            
            # Create two rows for better organization
            # Row 1: True/False activities
            bool_col1, bool_col2, bool_col3, bool_col4 = st.columns(4)
            
            with bool_col1:
                meditation_rate = activity_data[0] or 0
                gratitude_rate = activity_data[1] or 0
                st.markdown(f"""
                <div style="text-align: center; padding: 8px; background: rgba(99, 102, 241, 0.1); border-radius: 8px;">
                    <div style="font-size: 20px; font-weight: bold; color: #6366f1;">{meditation_rate:.0f}%</div>
                    <div style="font-size: 12px; color: #9ca3af;">🧘‍♂️ Meditation</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="text-align: center; padding: 8px; background: rgba(99, 102, 241, 0.1); border-radius: 8px; margin-top: 8px;">
                    <div style="font-size: 20px; font-weight: bold; color: #6366f1;">{gratitude_rate:.0f}%</div>
                    <div style="font-size: 12px; color: #9ca3af;">🙏 Gratitude</div>
                </div>
                """, unsafe_allow_html=True)
            
            with bool_col2:
                strength_rate = activity_data[2] or 0
                no_junk_rate = activity_data[7] or 0
                st.markdown(f"""
                <div style="text-align: center; padding: 8px; background: rgba(99, 102, 241, 0.1); border-radius: 8px;">
                    <div style="font-size: 20px; font-weight: bold; color: #6366f1;">{strength_rate:.0f}%</div>
                    <div style="font-size: 12px; color: #9ca3af;">💪 Strength</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="text-align: center; padding: 8px; background: rgba(99, 102, 241, 0.1); border-radius: 8px; margin-top: 8px;">
                    <div style="font-size: 20px; font-weight: bold; color: #6366f1;">{no_junk_rate:.0f}%</div>
                    <div style="font-size: 12px; color: #9ca3af;">🚫 No Junk</div>
                </div>
                """, unsafe_allow_html=True)
            
            with bool_col3:
                no_spending_rate = activity_data[3] or 0
                bitcoin_rate = activity_data[4] or 0
                st.markdown(f"""
                <div style="text-align: center; padding: 8px; background: rgba(99, 102, 241, 0.1); border-radius: 8px;">
                    <div style="font-size: 20px; font-weight: bold; color: #6366f1;">{no_spending_rate:.0f}%</div>
                    <div style="font-size: 12px; color: #9ca3af;">💰 No Spend</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="text-align: center; padding: 8px; background: rgba(99, 102, 241, 0.1); border-radius: 8px; margin-top: 8px;">
                    <div style="font-size: 20px; font-weight: bold; color: #6366f1;">{bitcoin_rate:.0f}%</div>
                    <div style="font-size: 12px; color: #9ca3af;">₿ Bitcoin</div>
                </div>
                """, unsafe_allow_html=True)
            
            with bool_col4:
                learning_rate = activity_data[5] or 0
                environmental_rate = activity_data[6] or 0
                st.markdown(f"""
                <div style="text-align: center; padding: 8px; background: rgba(99, 102, 241, 0.1); border-radius: 8px;">
                    <div style="font-size: 20px; font-weight: bold; color: #6366f1;">{learning_rate:.0f}%</div>
                    <div style="font-size: 12px; color: #9ca3af;">📚 Learning</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="text-align: center; padding: 8px; background: rgba(99, 102, 241, 0.1); border-radius: 8px; margin-top: 8px;">
                    <div style="font-size: 20px; font-weight: bold; color: #6366f1;">{environmental_rate:.0f}%</div>
                    <div style="font-size: 12px; color: #9ca3af;">🌍 Environment</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Row 2: Averages for numeric activities
            st.markdown("")  # Small spacing
            avg_col1, avg_col2, avg_col3 = st.columns(3)
            
            with avg_col1:
                avg_meals = activity_data[8] or 0
                st.markdown(f"""
                <div style="text-align: center; padding: 12px; background: linear-gradient(135deg, #10b981, #059669); border-radius: 8px; color: white;">
                    <div style="font-size: 24px; font-weight: bold;">{avg_meals:.1f}</div>
                    <div style="font-size: 12px;">🍳 Avg Meals/Day</div>
                </div>
                """, unsafe_allow_html=True)
            
            with avg_col2:
                avg_exercise = activity_data[9] or 0
                st.markdown(f"""
                <div style="text-align: center; padding: 12px; background: linear-gradient(135deg, #3b82f6, #2563eb); border-radius: 8px; color: white;">
                    <div style="font-size: 24px; font-weight: bold;">{avg_exercise:.0f}</div>
                    <div style="font-size: 12px;">🏃 Avg Minutes/Day</div>
                </div>
                """, unsafe_allow_html=True)
            
            with avg_col3:
                avg_sats = activity_data[10] or 0
                st.markdown(f"""
                <div style="text-align: center; padding: 12px; background: linear-gradient(135deg, #f59e0b, #d97706); border-radius: 8px; color: white;">
                    <div style="font-size: 24px; font-weight: bold;">{avg_sats:,.0f}</div>
                    <div style="font-size: 12px;">₿ Avg Sats/Day</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("")  # Spacing before achievements section

except Exception as e:
    # If there's an error, just skip this section
    pass


# Row 4: Achievements Summary
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🏆 Achievements")
    
    if earned_achievements:
        # Compact achievement summary
        total_achievements = len(earned_achievements)
        legendary_count = len([a for a in earned_achievements if a.get("rarity") == "legendary"])
        epic_count = len([a for a in earned_achievements if a.get("rarity") == "epic"])
        rare_count = len([a for a in earned_achievements if a.get("rarity") == "rare"])
        
        ach_cols = st.columns(4)
        
        with ach_cols[0]:
            st.metric("Total", total_achievements)
        with ach_cols[1]:
            st.metric("🌟 Legendary", legendary_count)
        with ach_cols[2]:
            st.metric("💜 Epic", epic_count)
        with ach_cols[3]:
            st.metric("💙 Rare", rare_count)
        
        # Show recent achievements inline
        recent_achievements = sorted(earned_achievements, key=lambda x: x.get("earned_date", ""), reverse=True)[:2]
        for achievement in recent_achievements:
            rarity = achievement.get("rarity", "common")
            st.markdown(f"""
            <div class="compact-achievement">
                <span class="achievement-badge {rarity}">{achievement['name']}</span>
                <small style="color: #6b7280; margin-left: 8px;">{achievement['description']}</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Expandable for full list
        with st.expander("View All Achievements"):
            by_rarity = {"legendary": [], "epic": [], "rare": [], "common": []}
            for ach in earned_achievements:
                rarity = ach.get("rarity", "common")
                if rarity in by_rarity:
                    by_rarity[rarity].append(ach)
            
            for rarity in ["legendary", "epic", "rare", "common"]:
                achievements = by_rarity[rarity]
                if achievements:
                    st.markdown(f"**{rarity.title()} ({len(achievements)})**")
                    for achievement in achievements:
                        st.markdown(f"• **{achievement['name']}** - {achievement['description']}")

with col2:
    st.markdown("### 🎯 Next Milestones")
    
    if next_achievements:
        for next_ach in next_achievements[:2]:
            progress_info = next_ach.get("progress", {})
            progress_pct = progress_info.get("progress", 0)
            
            st.markdown(f"""
            <div class="next-achievement-compact" style="padding: 8px;">
                <strong style="font-size: 12px;">{next_ach['name']}</strong>
                <div class="xp-progress-bar" style="height: 6px; margin: 4px 0;">
                    <div class="xp-progress-fill" style="width: {progress_pct}%;"></div>
                </div>
                <small>{progress_info.get('message', f'{progress_pct:.0f}% complete')}</small>
            </div>
            """, unsafe_allow_html=True)

# Row 5: Progress Charts (Compact)
st.markdown("---")
st.markdown("### 📈 Progress Analysis")

try:
    with get_db_connection() as conn:
        df = conn.execute("""
            SELECT timestamp, score, btc_sats
            FROM sovereignty 
            WHERE username = ?
            ORDER BY timestamp ASC
        """, [username]).df()

    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Score trend
            df['score_ma7'] = df['score'].rolling(window=7, min_periods=1).mean()
            
            fig_score = go.Figure()
            fig_score.add_trace(go.Scatter(
                x=df['timestamp'], 
                y=df['score_ma7'],
                mode='lines',
                name='7-Day Average',
                line=dict(color='#6366f1', width=3),
                hovertemplate='%{y:.1f} avg<br>%{x}<extra></extra>'
            ))
            
            fig_score.update_layout(
                title="Sovereignty Score Trend",
                height=250,
                margin=dict(l=0, r=0, t=30, b=0),
                showlegend=False
            )
            st.plotly_chart(fig_score, use_container_width=True)
        
        with chart_col2:
            # Bitcoin accumulation
            df['cumulative_sats'] = df['btc_sats'].fillna(0).cumsum()
            
            fig_btc = go.Figure()
            fig_btc.add_trace(go.Scatter(
                x=df['timestamp'], 
                y=df['cumulative_sats'],
                mode='lines',
                name='Sats',
                line=dict(color='#f59e0b', width=3),
                fill='tonexty',
                fillcolor='rgba(245, 158, 11, 0.1)'
            ))
            
            fig_btc.update_layout(
                title="Bitcoin Accumulation",
                height=250,
                margin=dict(l=0, r=0, t=30, b=0),
                showlegend=False
            )
            st.plotly_chart(fig_btc, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error loading chart data: {str(e)}")

# ═══════════════════════════════════════════════════════════════════
# 🧠 CONSCIOUSNESS EVOLUTION (COMPACT WILBER INTEGRATION)
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("### 🧠 Consciousness Evolution")

# Simple consciousness level display based on sovereignty data
consciousness_col1, consciousness_col2, consciousness_col3 = st.columns([2, 1, 1])

with consciousness_col1:
    # Determine consciousness level based on average score and days tracked
    avg_score = sovereignty_level.get('avg_score', 0)
    total_days = sovereignty_level.get('total_days', 0)
    
    if avg_score >= 80 and total_days >= 90:
        level_name = "🟢 Green - Community/Egalitarian"
        level_color = "#10b981"
        level_description = "Holistic sovereignty including environmental responsibility"
    elif avg_score >= 65 and total_days >= 60:
        level_name = "🟠 Orange - Rational/Achievement"
        level_color = "#f59e0b"
        level_description = "Systematic optimization of sovereignty metrics"
    elif avg_score >= 50 and total_days >= 30:
        level_name = "🟡 Amber - Rule/Order"
        level_color = "#eab308"
        level_description = "Following sovereignty principles consistently"
    else:
        level_name = "🔴 Red - Power/Action"
        level_color = "#ef4444"
        level_description = "Building personal power and sovereignty foundation"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {level_color}20, {level_color}10); 
                border: 2px solid {level_color}60; 
                border-radius: 12px; 
                padding: 16px;">
        <h4 style="margin: 0 0 8px 0; color: {level_color};">{level_name}</h4>
        <p style="margin: 0; color: #9ca3af; font-size: 13px;">{level_description}</p>
    </div>
    """, unsafe_allow_html=True)

with consciousness_col2:
    # Four Quadrants mini-display
    st.markdown("**🎯 AQAL Balance**")
    
    # Calculate quadrant scores based on user activities
    interior_score = min(100, earned_achievements.__len__() * 10)  # Based on achievements
    exterior_score = min(100, progress_metrics.get("total_tracking_days", 0))  # Based on tracking
    collective_score = 50  # Placeholder - would be based on community engagement
    systems_score = min(100, int(sats / 1000000 * 100))  # Based on financial sovereignty
    
    st.markdown(f"""
    <div style="font-size: 12px;">
        <div style="margin: 4px 0;">🧠 Interior: {interior_score}%</div>
        <div style="margin: 4px 0;">💪 Exterior: {exterior_score}%</div>
        <div style="margin: 4px 0;">🤝 Collective: {collective_score}%</div>
        <div style="margin: 4px 0;">⚙️ Systems: {systems_score}%</div>
    </div>
    """, unsafe_allow_html=True)

with consciousness_col3:
    # Development recommendations
    st.markdown("**📈 Growth Focus**")
    
    # Simple recommendations based on weakest quadrant
    recommendations = []
    if interior_score < 50:
        recommendations.append("🧘 Deepen meditation practice")
    if exterior_score < 50:
        recommendations.append("💪 Increase daily tracking")
    if systems_score < 50:
        recommendations.append("₿ Build financial sovereignty")
    
    if recommendations:
        for rec in recommendations[:2]:  # Show top 2
            st.markdown(f"<small style='color: #9ca3af;'>• {rec}</small>", unsafe_allow_html=True)
    else:
        st.markdown("<small style='color: #10b981;'>✨ Balanced development!</small>", unsafe_allow_html=True)


# Quick Actions
st.markdown("---")
action_col1, action_col2, action_col3, action_col4 = st.columns(4)

with action_col1:
    if st.button("📊 Track Today", type="primary", use_container_width=True):
        st.switch_page("app.py")

with action_col2:
    if st.button("🏆 Leaderboard", use_container_width=True):
        st.info("🔮 Coming soon!")

with action_col3:
    if st.button("🍳 Meal Planning", use_container_width=True):
        st.info("🥗 Coming soon!")

with action_col4:
    if st.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("👋 Logged out!")

# ═══════════════════════════════════════════════════════════════════
# SEASONAL EVENT (Moved to bottom as requested)
# ═══════════════════════════════════════════════════════════════════

# Check for active seasonal events
current_event = get_seasonal_event(datetime.now())

if current_event:
    st.markdown("---")
    
    with st.expander(f"🌟 {current_event['name']} - Active Event", expanded=False):
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {current_event['color']}20, {current_event['color']}10); 
                    border: 2px solid {current_event['color']}80; 
                    border-radius: 12px; 
                    padding: 16px;">
            <p style="margin: 0 0 8px 0; color: #6b7280; font-weight: bold;">
                {current_event['theme']}
            </p>
            <p style="margin: 0 0 12px 0; color: #374151;">
                {current_event['description']}
            </p>
            <div style="background: {current_event['color']}; color: white; 
                        padding: 6px 12px; border-radius: 16px; 
                        display: inline-block; font-weight: bold; font-size: 13px;">
                ⚡ {current_event['bonus']}
            </div>
            <p style="margin: 8px 0 0 0; color: #6b7280; font-size: 12px;">
                Event Period: {current_event['period']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Seasonal challenges
        seasonal_challenges = get_seasonal_challenges(current_event)
        
        if seasonal_challenges:
            st.markdown("**Special Event Challenges:**")
            
            for i, challenge in enumerate(seasonal_challenges):
                challenge_completed = st.checkbox(challenge, key=f"seasonal_{i}", value=False)

# Developer Mode (keep at very bottom)
if st.sidebar.checkbox("🔧 Developer Mode", value=False):
    with st.expander("🔧 XP System Debug Panel"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Award Test XP"):
                simple_engine = SimpleXPEngine()
                test_reference = f"debug_test_{datetime.now().strftime('%H%M%S')}"
                success = simple_engine.award_xp(username, 25, "debug", "Test XP award", test_reference)
                if success:
                    st.success("✅ Awarded 25 test XP!")
                    st.rerun()
        
        with col2:
            if st.button("Check XP Status"):
                simple_engine = SimpleXPEngine()
                xp_data = simple_engine.get_user_xp(username)
                st.json(xp_data)
        
        with col3:
            if st.button("Nuclear Reset"):
                if nuclear_reset_xp_system():
                    st.success("✅ XP system reset!")
                    st.balloons()

# Footer (compact)
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 12px; color: #6b7280; font-size: 14px;">
    <p>🛡️ <strong>Sovereignty is the new health plan.</strong></p>
    <small>Level {} • {:,} XP • {} Achievements</small>
</div>
""".format(gamification_data["current_level"], gamification_data["total_xp"], len(earned_achievements)), unsafe_allow_html=True)