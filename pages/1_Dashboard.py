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

try:
    from sovereignty_achievements import IntegratedSovereigntyEngine
    AQAL_AVAILABLE = True
except ImportError:
    AQAL_AVAILABLE = False

# Enhanced CSS for gamified sovereignty styling
st.markdown("""
<style>
    .gamification-hub {
        background: linear-gradient(135deg, #1f2937, #374151);
        border: 3px solid #6366f1;
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.3);
    }
    
    .xp-card {
        background: linear-gradient(45deg, #059669, #10b981);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin: 8px 0;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
    
    .level-card {
        background: linear-gradient(45deg, #7c3aed, #a78bfa);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin: 8px 0;
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);
    }
    
    .streak-card {
        background: linear-gradient(45deg, #ef4444, #f97316);
        color: white;
        padding: 16px;
        border-radius: 12px;
        text-align: center;
        margin: 8px 0;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
        transition: transform 0.2s;
    }
    
    .streak-card:hover {
        transform: scale(1.05);
    }
    
    .achievement-badge {
        display: inline-block;
        padding: 12px 20px;
        border-radius: 25px;
        margin: 6px;
        font-weight: bold;
        text-align: center;
        transition: transform 0.2s;
        cursor: pointer;
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
        padding: 16px;
        background: rgba(99, 102, 241, 0.1);
        border-radius: 12px;
        border: 2px solid rgba(99, 102, 241, 0.3);
        margin: 8px 0;
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
        padding: 12px;
        margin: 4px 0;
        font-size: 14px;
    }
    
    .next-achievement-compact {
        background: linear-gradient(135deg, #059669, #10b981);
        color: white;
        padding: 12px;
        border-radius: 8px;
        margin: 6px 0;
        font-size: 14px;
    }
    
    .financial-gamification {
        background: linear-gradient(135deg, #f59e0b, #fbbf24);
        color: #1f2937;
        padding: 16px;
        border-radius: 12px;
        margin: 8px 0;
        font-weight: bold;
    }
    
    .xp-progress-bar {
        background: rgba(255,255,255,0.3);
        border-radius: 10px;
        height: 12px;
        margin: 8px 0;
        overflow: hidden;
    }
    
    .xp-progress-fill {
        background: linear-gradient(45deg, #ffffff, #e5e7eb);
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
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

# Header with sovereignty branding
st.markdown(f"""
<div style="text-align: center; padding: 20px 0;">
    <h1 style="color: #6366f1; margin: 0;">🛡️ Sovereignty Dashboard</h1>
    <h3 style="color: #9ca3af; margin: 5px 0;">Welcome back, {username}</h3>
    <p style="color: #6b7280; margin: 0;">Path: {path.replace('_', ' ').title()}</p>
</div>
""", unsafe_allow_html=True)

# NEW: Initialize XP system
@st.cache_resource
def init_xp_engine():
    """Initialize and cache the XP engine"""
    return XPTransactionEngine()

# Initialize achievement engine
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_integrated_profile(username):
    """Get integrated sovereignty + AQAL profile"""
    if AQAL_AVAILABLE:
        engine = IntegratedSovereigntyEngine()
        return engine.calculate_complete_user_profile(username)
    return None

@st.cache_data(ttl=300)
def get_user_achievements(username):
    """Get user achievements with caching"""
    engine = SovereigntyAchievementEngine()
    return engine.calculate_user_achievements(username)

# NEW: Real XP calculation with legacy fallback
# Replace your calculate_gamification_metrics_real() function with this fixed version:

def calculate_gamification_metrics_real(username, achievements_data):
    """Calculate XP using ONLY the simple, reliable system"""
    
    # Always use simple XP system - no more complex system errors!
    return get_simple_gamification_data(username)

# Also add this improved error-handling version of your render function:

def render_xp_display_enhanced_safe(gamification_data):
    """Enhanced XP display with better error handling"""
    
    # Extract basic data with safe defaults
    total_xp = gamification_data.get("total_xp", 0)
    current_level = gamification_data.get("current_level", 1)
    xp_progress = gamification_data.get("xp_in_current_level", 0)
    today_xp = gamification_data.get("today_xp", 0)
    
    # Main XP display
    st.markdown('<div class="gamification-hub">', unsafe_allow_html=True)
    
    # Header with real-time XP
    header_col1, header_col2 = st.columns([2, 1])
    
    with header_col1:
        st.markdown(f"## 🎮 Level {current_level} Sovereign")
        st.markdown(f"**{total_xp:,} Total XP** • **+{today_xp} Today**")
    
    with header_col2:
        # XP gained indicator
        if today_xp > 0:
            st.markdown(f"""
            <div style="background: linear-gradient(45deg, #10b981, #059669); 
                        color: white; padding: 12px; border-radius: 8px; text-align: center;">
                <h3 style="margin: 0;">⚡ Active</h3>
                <p style="margin: 0; font-size: 14px;">+{today_xp} XP Today</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: rgba(107, 114, 128, 0.2); 
                        color: #6b7280; padding: 12px; border-radius: 8px; text-align: center;">
                <h3 style="margin: 0;">💤 Idle</h3>
                <p style="margin: 0; font-size: 14px;">No XP Today</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Enhanced progress bar
    st.markdown("**Progress to Next Level:**")
    progress_html = f"""
    <div style="background: rgba(255,255,255,0.1); border-radius: 12px; height: 20px; margin: 12px 0; overflow: hidden;">
        <div style="background: linear-gradient(45deg, #10b981, #059669); height: 20px; border-radius: 12px; width: {xp_progress}%; transition: width 0.3s ease;"></div>
    </div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #9ca3af;'>{xp_progress}/100 XP to Level {current_level + 1}</p>", unsafe_allow_html=True)
    
    # XP Breakdown (if available)
    breakdown = gamification_data.get("breakdown", [])
    recent_transactions = gamification_data.get("recent_transactions", [])
    
    if breakdown or recent_transactions:
        with st.expander("📊 XP Breakdown & Recent Activity"):
            
            # XP by source (if available)
            if breakdown:
                if len(breakdown) > 1:
                    breakdown_cols = st.columns(len(breakdown))
                    for i, source_data in enumerate(breakdown):
                        with breakdown_cols[i]:
                            source_emoji = {
                                "daily_challenge": "⚡",
                                "achievement": "🏆", 
                                "habit_tracking": "📝",
                                "legacy_migration": "🔄",
                                "streak_bonus": "🔥",
                                "simple": "🎯"
                            }
                            emoji = source_emoji.get(source_data.get("source", "simple"), "⭐")
                            
                            st.markdown(f"""
                            <div style="text-align: center; padding: 8px; background: rgba(99, 102, 241, 0.1); border-radius: 8px;">
                                <h3 style="margin: 0; color: #6366f1;">{emoji}</h3>
                                <p style="margin: 2px 0; font-size: 14px; font-weight: bold;">{source_data.get('xp', 0)} XP</p>
                                <p style="margin: 0; font-size: 12px; color: #6b7280;">{source_data.get('source', 'Unknown').replace('_', ' ').title()}</p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    # Single source breakdown
                    source_data = breakdown[0]
                    st.markdown(f"**Total XP:** {source_data.get('xp', 0)} from {source_data.get('source', 'tracking').replace('_', ' ').title()}")
            
            # Recent transactions (if available)
            if recent_transactions:
                st.markdown("**🕒 Recent XP Activity:**")
                for transaction in recent_transactions[:5]:
                    # Handle both simple and complex transaction formats
                    if isinstance(transaction, dict):
                        timestamp_str = "recently"
                        if "timestamp" in transaction and transaction["timestamp"]:
                            try:
                                timestamp = datetime.fromisoformat(str(transaction["timestamp"]))
                                timestamp_str = timestamp.strftime("%m/%d %I:%M%p")
                            except:
                                timestamp_str = "recently"
                        
                        multiplier = transaction.get('multiplier', 1.0)
                        multiplier_text = f" (x{multiplier})" if multiplier > 1.0 else ""
                        description = transaction.get('description', 'XP earned')
                        xp_amount = transaction.get('xp', 0)
                        
                        st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid rgba(107, 114, 128, 0.2);">
                            <span style="font-size: 12px; color: #374151;">{description}{multiplier_text}</span>
                            <span style="font-size: 12px; color: #10b981; font-weight: bold;">+{xp_amount} XP</span>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("Complete challenges to see recent XP activity!")
    
    st.markdown('</div>', unsafe_allow_html=True)

def migrate_legacy_xp(xp_engine, username, legacy_data):
    """One-time migration of legacy XP to new system"""
    try:
        # Migrate achievement XP
        if legacy_data["xp_breakdown"]["achievements"] > 0:
            xp_engine.award_xp(
                username=username,
                xp_amount=legacy_data["xp_breakdown"]["achievements"],
                source="legacy_migration",
                description="Migrated achievement XP from legacy system",
                reference_id="legacy_achievements"
            )
        
        # Migrate consistency XP (but cap it to prevent inflation)
        consistency_xp = min(legacy_data["xp_breakdown"]["consistency"], 500)  # Cap at 500
        if consistency_xp > 0:
            xp_engine.award_xp(
                username=username,
                xp_amount=consistency_xp,
                source="legacy_migration", 
                description="Migrated consistency XP from legacy system",
                reference_id="legacy_consistency"
            )
        
        print(f"✅ Migrated {username}'s legacy XP to new system")
        
    except Exception as e:
        print(f"❌ Error migrating legacy XP: {e}")

def calculate_gamification_metrics_legacy(username, achievements_data):
    """Your original gamification calculation as fallback"""
    earned_achievements = achievements_data.get("achievements_earned", [])
    progress_metrics = achievements_data.get("progress_metrics", {})
    
    # Base XP from achievements
    xp_from_achievements = 0
    rarity_xp = {"common": 10, "rare": 25, "epic": 50, "legendary": 100}
    
    for ach in earned_achievements:
        rarity = ach.get("rarity", "common")
        xp_from_achievements += rarity_xp.get(rarity, 10)
    
    # XP from tracking consistency
    total_days = progress_metrics.get("total_tracking_days", 0)
    xp_from_consistency = min(total_days * 5, 500)  # Cap to prevent inflation
    
    # XP from sovereignty actions
    meals_cooked = progress_metrics.get("total_meals_cooked", 0)
    sats_accumulated = progress_metrics.get("total_sats_accumulated", 0)
    
    xp_from_meals = min(meals_cooked * 3, 300)  # Cap at 300
    xp_from_sats = min(sats_accumulated // 10000, 200)  # Cap at 200
    
    # Total XP
    total_xp = xp_from_achievements + xp_from_consistency + xp_from_meals + xp_from_sats
    
    # Level calculation
    current_level = (total_xp // 100) + 1
    xp_in_current_level = total_xp % 100
    xp_to_next_level = 100 - xp_in_current_level
    
    return {
        "total_xp": total_xp,
        "current_level": current_level,
        "xp_in_current_level": xp_in_current_level,
        "xp_to_next_level": xp_to_next_level,
        "today_xp": 0,  # Legacy system doesn't track daily XP
        "xp_breakdown": {
            "achievements": xp_from_achievements,
            "consistency": xp_from_consistency,
            "meals": xp_from_meals,
            "sats": xp_from_sats
        }
    }

# NEW: Real daily challenges with XP integration
def render_daily_challenges_wrapper(username, path, current_streaks):
    """Wrapper to always use simple challenges"""
    render_simple_challenges(username, path, current_streaks)

# NEW: Enhanced XP display with real data
def render_xp_display_enhanced(gamification_data):
    """Enhanced XP display with transaction history"""
    
    total_xp = gamification_data["total_xp"]
    current_level = gamification_data["current_level"]
    xp_progress = gamification_data["xp_in_current_level"]
    today_xp = gamification_data["today_xp"]
    
    # Main XP display
    st.markdown('<div class="gamification-hub">', unsafe_allow_html=True)
    
    # Header with real-time XP
    header_col1, header_col2 = st.columns([2, 1])
    
    with header_col1:
        st.markdown(f"## 🎮 Level {current_level} Sovereign")
        st.markdown(f"**{total_xp:,} Total XP** • **+{today_xp} Today**")
    
    with header_col2:
        # XP gained indicator
        if today_xp > 0:
            st.markdown(f"""
            <div style="background: linear-gradient(45deg, #10b981, #059669); 
                        color: white; padding: 12px; border-radius: 8px; text-align: center;">
                <h3 style="margin: 0;">⚡ Active</h3>
                <p style="margin: 0; font-size: 14px;">+{today_xp} XP Today</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: rgba(107, 114, 128, 0.2); 
                        color: #6b7280; padding: 12px; border-radius: 8px; text-align: center;">
                <h3 style="margin: 0;">💤 Idle</h3>
                <p style="margin: 0; font-size: 14px;">No XP Today</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Enhanced progress bar
    st.markdown("**Progress to Next Level:**")
    progress_html = f"""
    <div style="background: rgba(255,255,255,0.1); border-radius: 12px; height: 20px; margin: 12px 0; overflow: hidden;">
        <div style="background: linear-gradient(45deg, #10b981, #059669); height: 20px; border-radius: 12px; width: {xp_progress}%; transition: width 0.3s ease;"></div>
    </div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #9ca3af;'>{xp_progress}/100 XP to Level {current_level + 1}</p>", unsafe_allow_html=True)
    
    # XP Breakdown (if available)
    if "breakdown" in gamification_data and gamification_data["breakdown"]:
        with st.expander("📊 XP Breakdown & Recent Activity"):
            
            # XP by source
            breakdown_cols = st.columns(len(gamification_data["breakdown"]))
            for i, source_data in enumerate(gamification_data["breakdown"]):
                with breakdown_cols[i]:
                    source_emoji = {
                        "daily_challenge": "⚡",
                        "achievement": "🏆", 
                        "habit_tracking": "📝",
                        "legacy_migration": "🔄",
                        "streak_bonus": "🔥"
                    }
                    emoji = source_emoji.get(source_data["source"], "⭐")
                    
                    st.markdown(f"""
                    <div style="text-align: center; padding: 8px; background: rgba(99, 102, 241, 0.1); border-radius: 8px;">
                        <h3 style="margin: 0; color: #6366f1;">{emoji}</h3>
                        <p style="margin: 2px 0; font-size: 14px; font-weight: bold;">{source_data['xp']} XP</p>
                        <p style="margin: 0; font-size: 12px; color: #6b7280;">{source_data['source'].replace('_', ' ').title()}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Recent transactions
            if "recent_transactions" in gamification_data and gamification_data["recent_transactions"]:
                st.markdown("**🕒 Recent XP Activity:**")
                for transaction in gamification_data["recent_transactions"][:5]:
                    timestamp = datetime.fromisoformat(str(transaction["timestamp"]))
                    multiplier_text = f" (x{transaction['multiplier']})" if transaction.get('multiplier', 1.0) > 1.0 else ""
                    
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid rgba(107, 114, 128, 0.2);">
                        <span style="font-size: 12px; color: #374151;">{transaction['description']}{multiplier_text}</span>
                        <span style="font-size: 12px; color: #10b981; font-weight: bold;">+{transaction['xp']} XP</span>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# NEW: Debug section for testing
def render_xp_debug_section(username):
    """Debug section for testing XP system - FIXED VERSION"""
    
    with st.expander("🔧 XP System Debug (Dev Only)"):
        st.markdown("**Quick XP Test Actions:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Award Test XP", key="debug_award_xp"):
                xp_engine = init_xp_engine()
                test_reference = f"debug_test_{datetime.now().strftime('%H%M%S')}"
                success = xp_engine.award_xp(username, 25, "debug", "Test XP award", test_reference)
                if success:
                    st.success("✅ Awarded 25 test XP!")
                    st.rerun()
                else:
                    st.error("❌ Error awarding XP")
        
        with col2:
            if st.button("Complete Test Challenge", key="debug_complete_challenge"):
                xp_engine = init_xp_engine()
                test_challenge_id = f"debug_challenge_{datetime.now().strftime('%H%M%S')}"
                success = xp_engine.complete_daily_challenge(username, test_challenge_id, "debug", 30)
                if success:
                    st.success("✅ Completed test challenge!")
                    st.rerun()
                else:
                    st.error("❌ Error completing challenge")
        
        with col3:
            if st.button("Check XP Status", key="debug_check_status"):
                xp_engine = init_xp_engine()
                xp_data = xp_engine.get_user_total_xp(username)
                st.json(xp_data)
        
        # Show recent XP transactions
        st.markdown("**Recent XP Transactions:**")
        xp_engine = init_xp_engine()
        raw_data = xp_engine.get_user_total_xp(username)
        
        if raw_data["recent_transactions"]:
            for txn in raw_data["recent_transactions"][:5]:
                st.markdown(f"• **+{txn['xp']} XP** from {txn['source']} - {txn['description']}")
        else:
            st.info("No XP transactions found")
# Add these functions after your existing function definitions (around line 200-300)

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
    
    # Generate challenges (reuse your existing function)
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
    
    st.markdown("**⚡ Daily Challenges** (Simple XP System)")
    
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

# CHANGED: Use the new real XP calculation
try:
    gamification_data = calculate_gamification_metrics_real(username, achievements_data)
except Exception as e:
    st.error(f"❌ XP System Error: {e}")
    # Fallback to simple system
    st.session_state['use_simple_xp'] = True
    gamification_data = get_simple_gamification_data(username)
    st.info("🔧 Switched to Simple XP System due to error")

# ALSO ADD this check right after your gamification_data calculation:
# Show XP system status
if st.session_state.get('use_simple_xp', False):
    st.info("🔧 Using Simple XP System - All features available!")
else:
    st.success("⚡ Using Advanced XP System")

integrated_profile = get_integrated_profile(username) if AQAL_AVAILABLE else None

# Extract achievement data
sovereignty_level = achievements_data.get("sovereignty_level", {})
earned_achievements = achievements_data.get("achievements_earned", [])
progress_metrics = achievements_data.get("progress_metrics", {})
next_achievements = achievements_data.get("next_achievements", [])
achievement_summary = achievements_data.get("achievement_summary", {})

# ═══════════════════════════════════════════════════════════════════
# 🌟 SEASONAL SOVEREIGNTY EVENTS
# ═══════════════════════════════════════════════════════════════════

# Check for active seasonal events
current_event = get_seasonal_event(datetime.now())

if current_event:
    st.markdown("---")
    
    # Event header with special styling
    event_type = "🎉 Special Event" if current_event["type"] == "special" else "🌟 Seasonal Event"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {current_event['color']}20, {current_event['color']}10); 
                border: 3px solid {current_event['color']}80; 
                border-radius: 16px; 
                padding: 24px; 
                margin: 16px 0;
                box-shadow: 0 8px 32px {current_event['color']}30;">
        <div style="text-align: center;">
            <h2 style="margin: 0 0 8px 0; color: {current_event['color']}; font-size: 24px;">
                {event_type}: {current_event['name']}
            </h2>
            <p style="margin: 0 0 8px 0; color: #6b7280; font-size: 16px; font-weight: bold;">
                {current_event['theme']}
            </p>
            <p style="margin: 0 0 12px 0; color: #374151; font-size: 14px;">
                {current_event['description']}
            </p>
            <div style="background: {current_event['color']}; color: white; 
                        padding: 8px 16px; border-radius: 20px; 
                        display: inline-block; font-weight: bold; font-size: 14px;">
                ⚡ {current_event['bonus']}
            </div>
            <p style="margin: 8px 0 0 0; color: #6b7280; font-size: 12px;">
                Event Period: {current_event['period']}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Seasonal challenges
    seasonal_challenges = get_seasonal_challenges(current_event)
    
    if seasonal_challenges:
        st.markdown("### 🎯 Special Event Challenges")
        st.markdown("*Complete these for bonus XP during the event!*")
        
        event_challenge_cols = st.columns(min(len(seasonal_challenges), 3))
        
        for i, challenge in enumerate(seasonal_challenges):
            col_idx = i % 3
            with event_challenge_cols[col_idx]:
                # Event-specific challenge styling
                challenge_completed = st.checkbox(f"Done", key=f"seasonal_{i}", value=False)
                
                if challenge_completed:
                    st.markdown(f"""
                    <div style="background: linear-gradient(45deg, {current_event['color']}, {current_event['color']}dd); 
                                color: white; padding: 12px; border-radius: 8px; margin: 4px 0;
                                border: 2px solid {current_event['color']}; text-align: center;
                                box-shadow: 0 4px 12px {current_event['color']}40;">
                        <h3 style="margin: 0; font-size: 16px;">✨ BONUS!</h3>
                        <p style="margin: 4px 0; font-size: 12px; opacity: 0.9;">{challenge}</p>
                        <p style="margin: 0; font-size: 14px; font-weight: bold;">+Extra XP</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, {current_event['color']}15, {current_event['color']}05); 
                                border: 2px solid {current_event['color']}60; 
                                border-radius: 8px; padding: 12px; margin: 4px 0; text-align: center;">
                        <h3 style="margin: 0; font-size: 16px; color: {current_event['color']};">⭐</h3>
                        <p style="margin: 4px 0; font-size: 13px; color: #374151; font-weight: bold;">Bonus XP</p>
                        <p style="margin: 0; font-size: 12px; color: #6b7280;">{challenge}</p>
                    </div>
                    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# 🎯 DAILY CHALLENGES & WEEKLY QUEST SECTION (CHANGED TO USE NEW SYSTEM)
# ═══════════════════════════════════════════════════════════════════

# Generate daily challenges and weekly quest
current_streaks = progress_metrics.get("current_streaks", {})

# Calculate week start for quest generation
from datetime import datetime, timedelta
today = datetime.now()
week_start = today - timedelta(days=today.weekday())
weekly_quest = generate_weekly_quest(username, path, week_start.strftime("%Y-%m-%d"))

st.markdown("---")
st.markdown("### 🎯 Today's Challenges & Weekly Quest")

# CHANGED: Use the new real challenge system
render_daily_challenges_wrapper(username, path, current_streaks)

# Weekly Quest Section (unchanged)
st.markdown("**🏆 Weekly Quest** (Resets Monday)")

# Mock progress calculation (in real app, this would be calculated from actual data)
quest_progress = 2  # Example: completed 2 out of target
quest_target = weekly_quest["target"]
quest_progress_pct = min(100, (quest_progress / quest_target) * 100)

quest_completed = quest_progress >= quest_target

# Create columns for better layout
quest_col1, quest_col2 = st.columns([3, 1])

with quest_col1:
    st.markdown(f"**{weekly_quest['name']}**")
    st.markdown(f"{weekly_quest['description']}")

with quest_col2:
    st.markdown(f"**{weekly_quest['xp']} XP**")
    st.markdown("Reward")

# Progress bar for weekly quest
if quest_completed:
    st.success("🎉 QUEST COMPLETED!")
    st.balloons()
else:
    quest_progress_bar = f"""
    <div style="background: rgba(139, 92, 246, 0.2); border-radius: 8px; height: 12px; margin: 8px 0;">
        <div style="background: linear-gradient(45deg, #8b5cf6, #7c3aed); height: 12px; border-radius: 8px; width: {quest_progress_pct}%;"></div>
    </div>
    """
    st.markdown(quest_progress_bar, unsafe_allow_html=True)
    st.markdown(f"**Progress:** {quest_progress}/{quest_target} ({quest_progress_pct:.0f}%)")

# Quick Challenge Tips (unchanged)
with st.expander("💡 Challenge Tips & Strategy"):
    st.markdown(f"""
    **Path-Specific Tips for {path.replace('_', ' ').title()}:**
    """)
    
    path_tips = {
        "financial_path": [
            "💰 Stack challenges early in the day for maximum willpower",
            "₿ Set up automatic DCA to easily complete Bitcoin challenges", 
            "🍳 Meal prep on weekends to dominate cooking challenges",
            "📚 Listen to finance podcasts during commute for learning challenges"
        ],
        "physical_optimization": [
            "💪 Schedule strength training for consistent completion",
            "🥩 Track protein intake to hit targets easily",
            "🍳 Prep high-protein snacks to avoid junk food temptation",
            "🏃 Morning exercise creates momentum for the entire day"
        ],
        "mental_resilience": [
            "🧘‍♂️ Start with just 5 minutes of meditation to build habit",
            "📚 Keep books nearby for easy learning opportunities",
            "🙏 Link gratitude to existing habits (morning coffee, bedtime)",
            "⚡ Focus on one high-value activity to boost scores quickly"
        ],
        "spiritual_growth": [
            "🌅 Create morning ritual combining meditation and gratitude",
            "🌍 Look for simple environmental actions (walk vs drive)",
            "📝 Keep a small journal for quick reflections",
            "🍽️ Practice mindful eating - no phones during meals"
        ],
        "planetary_stewardship": [
            "🌍 Small daily actions add up - choose one each morning",
            "♻️ Audit your waste stream to find reduction opportunities",
            "🥬 Shop local farmers markets for fresh, sustainable options",
            "🚲 Plan routes that allow walking/biking instead of driving"
        ],
        "default": [
            "⚖️ Focus on your strongest habits first to build momentum",
            "🎯 Combine activities - cook while listening to podcasts",
            "📈 Track everything to maximize consistency bonuses",
            "🔥 Protect your longest streaks - they're your biggest XP multipliers"
        ]
    }
    
    tips = path_tips.get(path, path_tips["default"])
    for tip in tips:
        st.markdown(f"- {tip}")
    
    st.markdown("""
    **Universal Challenge Strategies:**
    - 🌅 **Morning Momentum:** Complete challenges early when willpower is highest
    - ⚡ **Stack Habits:** Combine multiple challenges into single activities
    - 🔄 **Backup Plans:** Have easy fallback options for busy days
    - 🎯 **Focus:** Better to complete 2 challenges well than attempt all 3 poorly
    """)

# ═══════════════════════════════════════════════════════════════════
# 🏆 SOVEREIGNTY LEVEL + 🎮 GAMIFICATION HUB (CHANGED TO USE NEW SYSTEM)
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")

# Compact level + XP display using Streamlit components
level_name = sovereignty_level.get('name', 'Unknown Level')
avg_score = sovereignty_level.get('avg_score', 0)
total_days = sovereignty_level.get('total_days', 0)

# CHANGED: Use the new enhanced XP display
render_xp_display_enhanced_safe(gamification_data)

# ═══════════════════════════════════════════════════════════════════
# REST OF THE DASHBOARD REMAINS UNCHANGED
# ═══════════════════════════════════════════════════════════════════

# 📊 SOVEREIGNTY METRICS
st.markdown("### 📊 Sovereignty Metrics")

metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)

with metrics_col1:
    sats = progress_metrics.get("total_sats_accumulated", 0)
    # Calculate financial sovereignty score
    btc_to_whole = max(0, 100000000 - sats)
    sats_progress = min(100, (sats / 100000000) * 100)
    
    st.markdown(f"""
    <div class="sovereignty-metric">
        <h3 style="margin: 0; color: #f59e0b;">₿ {sats:,}</h3>
        <p style="margin: 5px 0; color: #9ca3af;">Sats Stacked</p>
        <small style="color: #6b7280;">{sats_progress:.1f}% to whole coin</small>
    </div>
    """, unsafe_allow_html=True)

with metrics_col2:
    meals = progress_metrics.get("total_meals_cooked", 0)
    # Calculate meal sovereignty score
    meal_savings = meals * 12  # $12 average savings per meal
    
    st.markdown(f"""
    <div class="sovereignty-metric">
        <h3 style="margin: 0; color: #10b981;">🍳 {meals}</h3>
        <p style="margin: 5px 0; color: #9ca3af;">Meals Cooked</p>
        <small style="color: #6b7280;">${meal_savings:,} saved</small>
    </div>
    """, unsafe_allow_html=True)

with metrics_col3:
    btc_invested = progress_metrics.get("total_btc_invested", 0)
    st.markdown(f"""
    <div class="sovereignty-metric">
        <h3 style="margin: 0; color: #3b82f6;">${btc_invested:,.0f}</h3>
        <p style="margin: 5px 0; color: #9ca3af;">BTC Invested</p>
    </div>
    """, unsafe_allow_html=True)

with metrics_col4:
    tracking_days = progress_metrics.get("total_tracking_days", 0)
    consistency_rate = min(100, (tracking_days / max(1, (datetime.now() - datetime(2024, 1, 1)).days)) * 100)
    
    st.markdown(f"""
    <div class="sovereignty-metric">
        <h3 style="margin: 0; color: #8b5cf6;">📅 {tracking_days}</h3>
        <p style="margin: 5px 0; color: #9ca3af;">Days Tracked</p>
        <small style="color: #6b7280;">{consistency_rate:.0f}% consistency</small>
    </div>
    """, unsafe_allow_html=True)

# Financial Gamification Banner
if sats > 0 or btc_invested > 0:
    total_financial_sovereignty = meal_savings + btc_invested
    st.markdown(f"""
    <div class="financial-gamification">
        💰 <strong>Financial Sovereignty Achieved:</strong> ${total_financial_sovereignty:,}
        <br><small>🏆 Every sovereign choice compounds your freedom</small>
    </div>
    """, unsafe_allow_html=True)

# 🏆 CONDENSED ACHIEVEMENT SHOWCASE
st.markdown("---")
st.markdown("### 🏆 Achievement Collection")

if earned_achievements:
    # Show achievement summary first
    total_achievements = len(earned_achievements)
    legendary_count = len([a for a in earned_achievements if a.get("rarity") == "legendary"])
    epic_count = len([a for a in earned_achievements if a.get("rarity") == "epic"])
    
    summary_col1, summary_col2, summary_col3 = st.columns(3)
    
    with summary_col1:
        st.markdown(f"""
        <div class="xp-card">
            <h3 style="margin: 0;">🏅 {total_achievements}</h3>
            <p style="margin: 5px 0;">Total Earned</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col2:
        st.markdown(f"""
        <div class="level-card">
            <h3 style="margin: 0;">🌟 {legendary_count}</h3>
            <p style="margin: 5px 0;">Legendary</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col3:
        st.markdown(f"""
        <div class="streak-card">
            <h3 style="margin: 0;">💜 {epic_count}</h3>
            <p style="margin: 5px 0;">Epic</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Show recent achievements (last 3)
    st.markdown("**🔥 Recent Achievements:**")
    recent_achievements = sorted(earned_achievements, key=lambda x: x.get("earned_date", ""), reverse=True)[:3]
    
    for achievement in recent_achievements:
        rarity = achievement.get("rarity", "common")
        st.markdown(f"""
        <div class="compact-achievement">
            <strong>{achievement['name']}</strong>
            <span class="achievement-badge {rarity}" style="font-size: 12px; padding: 4px 8px; margin-left: 8px;">
                {rarity.title()}
            </span>
            <br><small style="color: #6b7280;">{achievement['description']}</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Expandable full achievement list
    with st.expander("🎖️ View All Achievements"):
        by_rarity = {"legendary": [], "epic": [], "rare": [], "common": []}
        for ach in earned_achievements:
            rarity = ach.get("rarity", "common")
            if rarity in by_rarity:
                by_rarity[rarity].append(ach)
        
        for rarity in ["legendary", "epic", "rare", "common"]:
            achievements = by_rarity[rarity]
            if achievements:
                rarity_emoji = {"legendary": "🌟", "epic": "💜", "rare": "💙", "common": "🔘"}
                st.markdown(f"**{rarity_emoji[rarity]} {rarity.title()} ({len(achievements)})**")
                
                ach_cols = st.columns(min(len(achievements), 2))
                for i, achievement in enumerate(achievements):
                    col_idx = i % 2
                    with ach_cols[col_idx]:
                        st.markdown(f"""
                        <div class="achievement-badge {rarity}" style="font-size: 13px; display: block; margin: 4px 0;">
                            {achievement['name']}<br>
                            <small>{achievement['description']}</small>
                        </div>
                        """, unsafe_allow_html=True)
else:
    st.info("🎯 Start tracking consistently to earn your first achievements!")

# CONTINUATION FROM WHERE YOUR CODE LEFT OFF...
# This preserves ALL your existing sections and adds the XP integration

# 🎯 NEXT ACHIEVEMENTS PREVIEW
if next_achievements:
    st.markdown("**🎯 Next Achievements:**")
    
    next_col1, next_col2 = st.columns(2)
    
    for i, next_ach in enumerate(next_achievements[:4]):  # Show top 4
        col = next_col1 if i % 2 == 0 else next_col2
        with col:
            progress = next_ach.get("progress", {})
            progress_pct = progress.get("progress", 0)
            
            st.markdown(f"""
            <div class="next-achievement-compact">
                <strong>{next_ach['name']}</strong>
                <div style="background: rgba(255,255,255,0.3); border-radius: 6px; height: 8px; margin: 4px 0;">
                    <div style="background: white; height: 8px; border-radius: 6px; width: {progress_pct}%;"></div>
                </div>
                <small>{progress.get('message', f'{progress_pct:.0f}% complete')}</small>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# 🔥 CONDENSED ACTIVE STREAKS (FROM YOUR EXISTING CODE)
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("### 🔥 Active Streaks")

current_streaks = progress_metrics.get("current_streaks", {})
active_streaks = {k: v for k, v in current_streaks.items() if v > 0}

if active_streaks:
    # Show top 3 streaks prominently
    top_streaks = sorted(active_streaks.items(), key=lambda x: x[1], reverse=True)[:3]
    
    streak_cols = st.columns(len(top_streaks))
    for i, (activity, days) in enumerate(top_streaks):
        with streak_cols[i]:
            activity_emoji = {
                "meditation": "🧘‍♂️",
                "gratitude": "🙏",
                "strength_training": "💪",
                "invested_bitcoin": "₿",
                "environmental_action": "🌍",
                "cooking": "👨‍🍳"
            }
            emoji = activity_emoji.get(activity, "⚡")
            
            # Calculate streak multiplier for XP
            streak_multiplier = 1 + (days // 7) * 0.1  # 10% bonus per week
            
            st.markdown(f"""
            <div class="streak-card">
                <h2 style="margin: 0;">{emoji}</h2>
                <h3 style="margin: 5px 0;">{days} Days</h3>
                <p style="margin: 0; font-size: 14px;">{activity.replace('_', ' ').title()}</p>
                <small style="opacity: 0.8;">{streak_multiplier:.1f}x XP Bonus</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Show other streaks compactly
    other_streaks = dict(sorted(active_streaks.items(), key=lambda x: x[1], reverse=True)[3:])
    if other_streaks:
        st.markdown("**Other Active Streaks:**")
        other_cols = st.columns(min(len(other_streaks), 4))
        for i, (activity, days) in enumerate(other_streaks.items()):
            col_idx = i % 4
            with other_cols[col_idx]:
                emoji = activity_emoji.get(activity, "⚡")
                st.markdown(f"**{emoji} {days}** {activity.replace('_', ' ').title()}")
else:
    st.info("💡 Start a new streak today! Every sovereignty journey begins with a single step.")

# ═══════════════════════════════════════════════════════════════════
# 🎯 CONDENSED NEXT ACHIEVEMENTS (FROM YOUR EXISTING CODE)
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("### 🎯 Next Milestones")

if next_achievements:
    # Show top 2 next achievements compactly
    for next_ach in next_achievements[:2]:
        progress_info = next_ach.get("progress", {})
        progress_pct = progress_info.get("progress", 0)
        
        st.markdown(f"""
        <div class="next-achievement-compact">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>{next_ach['name']}</strong>
                    <br><small style="opacity: 0.9;">{progress_info.get('message', f'{progress_pct:.0f}% complete')}</small>
                </div>
                <div style="text-align: right;">
                    <strong>{progress_pct:.0f}%</strong>
                </div>
            </div>
            <div style="background: rgba(255,255,255,0.3); border-radius: 8px; height: 6px; margin: 8px 0;">
                <div style="background: #ffffff; height: 6px; border-radius: 8px; width: {progress_pct}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Show remaining in expandable section
    if len(next_achievements) > 2:
        with st.expander(f"📋 View {len(next_achievements) - 2} More Upcoming Achievements"):
            for next_ach in next_achievements[2:]:
                progress_info = next_ach.get("progress", {})
                progress_pct = progress_info.get("progress", 0)
                st.markdown(f"**{next_ach['name']}** - {progress_pct:.0f}% ({progress_info.get('message', 'In progress')})")
else:
    st.info("🎉 You're on track! Keep building those sovereignty habits.")

# ═══════════════════════════════════════════════════════════════════
# 📈 PROGRESS ANALYSIS (YOUR EXISTING CODE - UNCHANGED)
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("## 📈 Progress Analysis")

# Load detailed data for charts
try:
    with get_db_connection() as conn:
        df = conn.execute("""
            SELECT timestamp, score, 
                home_cooked_meals, junk_food, exercise_minutes, 
                strength_training, no_spending, invested_bitcoin,
                btc_usd, btc_sats,
                meditation, gratitude, read_or_learned, 
                environmental_action
            FROM sovereignty 
            WHERE username = ?
            ORDER BY timestamp ASC
        """, [username]).df()

    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Score trend with 7-day moving average
            df['score_ma7'] = df['score'].rolling(window=7, min_periods=1).mean()
            
            fig_score = go.Figure()
            fig_score.add_trace(go.Scatter(
                x=df['timestamp'], 
                y=df['score'],
                mode='markers',
                name='Daily Score',
                marker=dict(color='rgba(99, 102, 241, 0.6)', size=4),
                hovertemplate='%{y:.0f} points<br>%{x}<extra></extra>'
            ))
            fig_score.add_trace(go.Scatter(
                x=df['timestamp'], 
                y=df['score_ma7'],
                mode='lines',
                name='7-Day Average',
                line=dict(color='#6366f1', width=3),
                hovertemplate='%{y:.1f} avg<br>%{x}<extra></extra>'
            ))
            
            fig_score.update_layout(
                title="🎯 Sovereignty Score Progression",
                xaxis_title="Date",
                yaxis_title="Score",
                hovermode='x unified',
                showlegend=True,
                height=400
            )
            st.plotly_chart(fig_score, use_container_width=True)
        
        with chart_col2:
            # Bitcoin accumulation over time
            df['cumulative_sats'] = df['btc_sats'].fillna(0).cumsum()
            
            fig_btc = go.Figure()
            fig_btc.add_trace(go.Scatter(
                x=df['timestamp'], 
                y=df['cumulative_sats'],
                mode='lines',
                name='Sats Accumulated',
                line=dict(color='#f59e0b', width=3),
                fill='tonexty',
                fillcolor='rgba(245, 158, 11, 0.1)',
                hovertemplate='%{y:,} sats<br>%{x}<extra></extra>'
            ))
            
            # Add milestone lines
            milestones = [100000, 1000000, 10000000, 25000000, 50000000, 100000000]
            milestone_names = ["100K", "1M", "10M", "25M (Quarter)", "50M (Half)", "100M (Whole)"]
            
            max_sats = df['cumulative_sats'].max() if not df['cumulative_sats'].empty else 0
            for milestone, name in zip(milestones, milestone_names):
                if milestone <= max_sats * 1.2:  # Show milestones up to 20% above current
                    fig_btc.add_hline(
                        y=milestone,
                        line_dash="dash",
                        line_color="rgba(245, 158, 11, 0.5)",
                        annotation_text=name,
                        annotation_position="right"
                    )
            
            fig_btc.update_layout(
                title="₿ Bitcoin Accumulation Journey",
                xaxis_title="Date",
                yaxis_title="Cumulative Sats",
                hovermode='x unified',
                height=400
            )
            st.plotly_chart(fig_btc, use_container_width=True)

        # Habit heatmap for last 60 days
        st.markdown("### 🔥 Recent Activity Heatmap")
        
        # Get last 60 days
        last_60_days = df[df['timestamp'] >= datetime.now() - timedelta(days=60)].copy()
        
        if not last_60_days.empty:
            # Create heatmap data
            habits_for_heatmap = ['meditation', 'gratitude', 'strength_training', 'invested_bitcoin', 'environmental_action']
            habit_labels = ['Meditation', 'Gratitude', 'Strength', 'Bitcoin', 'Environment']
            
            # Prepare data for heatmap
            heatmap_data = []
            for habit in habits_for_heatmap:
                heatmap_data.append(last_60_days[habit].astype(int).values)
            
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=heatmap_data,
                y=habit_labels,
                x=last_60_days['timestamp'].dt.strftime('%m-%d').values,
                colorscale=[[0, '#1f2937'], [1, '#6366f1']],
                showscale=False,
                hovertemplate='%{y}<br>%{x}<br>%{z}<extra></extra>'
            ))
            
            fig_heatmap.update_layout(
                title="📅 Activity Heatmap (Last 60 Days)",
                xaxis_title="Date",
                yaxis_title="Activity",
                height=300
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error loading chart data: {str(e)}")

# ═══════════════════════════════════════════════════════════════════
# 🧠 CONSCIOUSNESS DEVELOPMENT (AQAL) - IF AVAILABLE
# ═══════════════════════════════════════════════════════════════════

if AQAL_AVAILABLE and integrated_profile and "error" not in integrated_profile:
    # Extract AQAL data
    aqal_data = integrated_profile.get("aqal_consciousness", {})
    if aqal_data and "error" not in aqal_data:
        consciousness_level = aqal_data.get("consciousness_level", {})
        quadrant_development = aqal_data.get("quadrant_development", {})
        unified_progress = integrated_profile.get("unified_progress_score", {})
        
        st.markdown("---")
        st.markdown("## 🧠 Consciousness Development (Wilber AQAL)")
        
        # Consciousness Level & Unified Progress
        consciousness_col1, consciousness_col2 = st.columns([2, 1])
        
        with consciousness_col1:
            level_name = consciousness_level.get("name", "🔴 Red - Power/Action")
            sovereignty_focus = consciousness_level.get("sovereignty_focus", "Personal power development")
            characteristic = consciousness_level.get("characteristic", "Developing")
            
            # Determine level color based on name
            level_colors = {
                "Red": "#FF0000", "Amber": "#FFBF00", "Orange": "#FF8C00", 
                "Green": "#32CD32", "Teal": "#008080", "Turquoise": "#40E0D0"
            }
            level_color = "#6366f1"  # default
            for color_key, color_value in level_colors.items():
                if color_key in level_name:
                    level_color = color_value
                    break
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {level_color}20, {level_color}10); 
                        border: 2px solid {level_color}60; 
                        border-radius: 12px; 
                        padding: 20px; 
                        text-align: center;">
                <h3 style="margin: 0 0 12px 0; color: {level_color};">{level_name}</h3>
                <p style="margin: 0 0 8px 0; color: #6b7280; font-size: 14px;">
                    <strong>Focus:</strong> {sovereignty_focus}
                </p>
                <p style="margin: 0; color: #9ca3af; font-size: 13px;">
                    {characteristic} Consciousness
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with consciousness_col2:
            unified_score = unified_progress.get("unified_score", 0)
            integration_level = unified_progress.get("integration_level", "Developing")
            
            st.markdown(f"""
            <div class="sovereignty-metric">
                <h2 style="margin: 0; color: #8b5cf6;">{unified_score:.1f}</h2>
                <p style="margin: 5px 0; color: #9ca3af;">Unified Progress</p>
                <p style="margin: 0; font-size: 12px; color: #6b7280;">{integration_level}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # AQAL Four Quadrants Mini-Display
        st.markdown("### 🎯 AQAL Four Quadrants Development")
        
        quad_col1, quad_col2, quad_col3, quad_col4 = st.columns(4)
        
        quadrant_info = [
            ("upper_left", "🧠 Interior (I)", "Consciousness"),
            ("upper_right", "💪 Exterior (IT)", "Behaviors"), 
            ("lower_left", "🤝 Culture (WE)", "Relationships"),
            ("lower_right", "⚙️ Systems (ITS)", "Environment")
        ]
        
        for i, (quad_id, quad_name, quad_focus) in enumerate(quadrant_info):
            quad_data = quadrant_development.get(quad_id, {})
            quad_score = quad_data.get("performance_score", 0)
            quad_level = quad_data.get("development_level", "Developing")
            
            col = [quad_col1, quad_col2, quad_col3, quad_col4][i]
            with col:
                st.markdown(f"""
                <div style="background: rgba(99, 102, 241, 0.1); 
                            border: 1px solid rgba(99, 102, 241, 0.3); 
                            border-radius: 8px; 
                            padding: 12px; 
                            text-align: center;
                            margin: 4px 0;">
                    <h4 style="margin: 0 0 8px 0; color: #6366f1; font-size: 14px;">{quad_name}</h4>
                    <p style="margin: 0 0 4px 0; font-size: 12px; color: #9ca3af;">{quad_focus}</p>
                    <h3 style="margin: 0 0 4px 0; color: #6366f1;">{quad_score:.0f}</h3>
                    <p style="margin: 0; font-size: 11px; color: #6b7280;">{quad_level}</p>
                </div>
                """, unsafe_allow_html=True)

        # AQAL Achievements & Insights
        aqal_achievements = aqal_data.get("aqal_achievements", [])
        integrated_insights = integrated_profile.get("integrated_insights", [])
        recommendations = integrated_profile.get("development_recommendations", [])
        
        if aqal_achievements or integrated_insights:
            st.markdown("---")
            st.markdown("## 🌟 Consciousness Achievements & Insights")
            
            insights_col1, insights_col2 = st.columns([1, 1])
            
            with insights_col1:
                st.markdown("### 🧠 AQAL Consciousness Achievements")
                
                if aqal_achievements:
                    # Group AQAL achievements by rarity
                    aqal_rarities = {"aqal_legendary": [], "aqal_epic": [], "aqal_rare": [], "aqal_common": []}
                    for ach in aqal_achievements:
                        rarity = ach.get("rarity", "aqal_common")
                        if rarity in aqal_rarities:
                            aqal_rarities[rarity].append(ach)
                    
                    # Display AQAL achievements
                    aqal_rarity_colors = {
                        "aqal_legendary": "#f59e0b", 
                        "aqal_epic": "#8b5cf6", 
                        "aqal_rare": "#3b82f6", 
                        "aqal_common": "#6b7280"
                    }
                    
                    aqal_rarity_names = {
                        "aqal_legendary": "🌟 Legendary", 
                        "aqal_epic": "💜 Epic", 
                        "aqal_rare": "🔵 Rare", 
                        "aqal_common": "🔘 Common"
                    }
                    
                    for rarity, achievements in aqal_rarities.items():
                        if achievements:
                            color = aqal_rarity_colors[rarity]
                            name = aqal_rarity_names[rarity]
                            
                            st.markdown(f"**{name} Consciousness ({len(achievements)})**")
                            for achievement in achievements[:2]:  # Show max 2 per rarity
                                quadrant = achievement.get("quadrant", "general").replace("_", " ").title()
                                level = achievement.get("level", "").title()
                                
                                st.markdown(f"""
                                <div style="background: linear-gradient(45deg, {color}20, {color}10); 
                                            border: 1px solid {color}60; 
                                            border-radius: 8px; 
                                            padding: 12px; 
                                            margin: 6px 0;">
                                    <h5 style="margin: 0 0 4px 0; color: {color};">{achievement['name']}</h5>
                                    <p style="margin: 0 0 4px 0; font-size: 12px; color: #6b7280;">
                                        {achievement['consciousness_marker']}
                                    </p>
                                    <p style="margin: 0; font-size: 11px; color: #9ca3af;">
                                        {quadrant} • {level} Level
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                else:
                    st.info("🎯 Continue developing consciousness through sovereignty practices to unlock AQAL achievements!")
            
            with insights_col2:
                st.markdown("### 💡 Integrated Development Insights")
                
                # Show integrated insights
                if integrated_insights:
                    for insight in integrated_insights[:3]:  # Show top 3 insights
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.1)); 
                                    border-left: 4px solid #10b981; 
                                    padding: 12px; 
                                    margin: 8px 0; 
                                    border-radius: 0 8px 8px 0;">
                            <p style="margin: 0; font-size: 14px; color: #374151; line-height: 1.4;">
                                💡 {insight}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Show development recommendations
                st.markdown("**🎯 Development Recommendations:**")
                if recommendations:
                    for rec in recommendations[:3]:  # Show top 3 recommendations
                        st.markdown(f"""
                        <div style="background: rgba(139, 92, 246, 0.1); 
                                    border-left: 3px solid #8b5cf6; 
                                    padding: 10px; 
                                    margin: 6px 0; 
                                    border-radius: 0 6px 6px 0;">
                            <p style="margin: 0; font-size: 13px; color: #4b5563;">
                                📋 {rec}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Continue tracking to receive personalized development recommendations!")

elif AQAL_AVAILABLE:
    st.markdown("---")
    st.markdown("## 🧠 Consciousness Development")
    st.info("🔮 Enable AQAL consciousness tracking by updating your sovereignty achievements engine!")
else:
    # Add a teaser section for non-AQAL users
    st.markdown("---")
    st.markdown("## 🧠 Unlock Consciousness Development")
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(99, 102, 241, 0.1)); 
                border: 2px solid rgba(139, 92, 246, 0.3); 
                border-radius: 12px; 
                padding: 20px; 
                text-align: center;">
        <h3 style="color: #8b5cf6; margin: 0 0 12px 0;">🚀 Coming Soon: AQAL Consciousness Tracking</h3>
        <p style="margin: 0 0 12px 0; color: #6b7280;">
            Track your consciousness development through Ken Wilber's Integral AQAL framework alongside your sovereignty habits.
        </p>
        <p style="margin: 0; font-size: 14px; color: #9ca3af;">
            🎯 Four Quadrants Development • 🌀 Consciousness Levels • 📈 Lines of Development • 💎 Integral Achievements
        </p>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# 🎮 XP LEADERBOARD (OPTIONAL - COMPETITIVE USERS)
# ═══════════════════════════════════════════════════════════════════

def render_xp_leaderboard():
    """Optional leaderboard for competitive users"""
    
    with st.expander("🏆 Sovereignty Leaderboard (Anonymous)"):
        st.markdown("**🎯 This Week's Top Sovereigns:**")
        
        # Mock leaderboard data (in real app, this would come from database)
        leaderboard_data = [
            {"rank": 1, "name": "Sovereign_Alpha", "xp": 847, "level": 9, "path": "Financial"},
            {"rank": 2, "name": "BitcoinMonk", "xp": 723, "level": 8, "path": "Mental"},
            {"rank": 3, "name": "IronSovereign", "xp": 689, "level": 7, "path": "Physical"},
            {"rank": 4, "name": "PlanetGuardian", "xp": 612, "level": 7, "path": "Planetary"},
            {"rank": 5, "name": "SovereignSeeker", "xp": 534, "level": 6, "path": "Spiritual"}
        ]
        
        for entry in leaderboard_data:
            rank_emoji = {1: "🥇", 2: "🥈", 3: "🥉"}.get(entry["rank"], "🏅")
            
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; 
                        padding: 8px 12px; margin: 4px 0; 
                        background: rgba(99, 102, 241, 0.05); 
                        border-radius: 8px; border: 1px solid rgba(99, 102, 241, 0.2);">
                <div>
                    <strong>{rank_emoji} #{entry['rank']} {entry['name']}</strong>
                    <small style="color: #6b7280; margin-left: 8px;">{entry['path']} Path</small>
                </div>
                <div style="text-align: right;">
                    <strong style="color: #6366f1;">Lvl {entry['level']}</strong>
                    <small style="color: #9ca3af; margin-left: 8px;">{entry['xp']} XP</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <small style="color: #6b7280;">
        🔒 Privacy: All names are anonymous handles. Real names never shown.
        </small>
        """, unsafe_allow_html=True)

# Add leaderboard
render_xp_leaderboard()

# ═══════════════════════════════════════════════════════════════════
# ⚡ QUICK ACTIONS (FROM YOUR EXISTING CODE)
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("## ⚡ Quick Actions")

action_col1, action_col2, action_col3 = st.columns(3)

with action_col1:
    if st.button("📊 Track Today", type="primary", use_container_width=True):
        st.switch_page("app.py")

with action_col2:
    if st.button("🧠 View AI Insights", use_container_width=True):
        st.info("🔮 AI Coaching insights coming soon!")

with action_col3:
    if st.button("🍳 Meal Planning", use_container_width=True):
        st.info("🥗 AI meal planning coming soon!")

# ═══════════════════════════════════════════════════════════════════
# 🔧 UNIFIED DEBUG SECTION (REMOVE IN PRODUCTION)
# ═══════════════════════════════════════════════════════════════════

# REMOVE THIS SECTION BEFORE PRODUCTION DEPLOYMENT
if st.sidebar.checkbox("🔧 Developer Mode", value=False):
    
    st.markdown("---")
    st.markdown("## 🔧 XP System Debug Panel")
    
    # ═══ SIMPLE XP TESTING ═══
    with st.expander("🧪 Simple XP Tests"):
        st.markdown("**Quick XP Test Actions:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Award Test XP", key="debug_award_xp"):
                simple_engine = SimpleXPEngine()
                test_reference = f"debug_test_{datetime.now().strftime('%H%M%S')}"
                success = simple_engine.award_xp(username, 25, "debug", "Test XP award", test_reference)
                if success:
                    st.success("✅ Awarded 25 test XP!")
                    st.rerun()
                else:
                    st.error("❌ Error awarding XP")
        
        with col2:
            if st.button("Complete Test Challenge", key="debug_complete_challenge"):
                simple_engine = SimpleXPEngine()
                test_challenge_id = f"debug_challenge_{datetime.now().strftime('%H%M%S')}"
                success = simple_engine.complete_challenge(username, test_challenge_id, "debug", 30)
                if success:
                    st.success("✅ Completed test challenge!")
                    st.rerun()
                else:
                    st.error("❌ Error completing challenge")
        
        with col3:
            if st.button("Check XP Status", key="debug_check_status"):
                simple_engine = SimpleXPEngine()
                xp_data = simple_engine.get_user_xp(username)
                st.json(xp_data)
        
        # Show recent XP transactions
        st.markdown("**Recent XP Transactions:**")
        simple_engine = SimpleXPEngine()
        raw_data = simple_engine.get_user_xp(username)
        
        if raw_data["recent_transactions"]:
            for txn in raw_data["recent_transactions"][:5]:
                st.markdown(f"• **+{txn['xp']} XP** from {txn['source']} - {txn['description']}")
        else:
            st.info("No XP transactions found")
    
    # ═══ NUCLEAR RESET SECTION ═══ 
    with st.expander("💥 NUCLEAR XP RESET (Use if XP system is broken)"):
        st.warning("⚠️ This will DELETE ALL XP data and recreate tables!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💥 NUCLEAR RESET", type="secondary", key="nuclear_reset_btn"):
                if nuclear_reset_xp_system():
                    st.success("✅ XP system reset! Refresh page.")
                    st.balloons()
                else:
                    st.error("❌ Reset failed")
        
        with col2:
            if st.button("🧪 Test Simple XP", key="test_simple_xp_btn"):
                simple_engine = SimpleXPEngine()
                success = simple_engine.award_xp(username, 25, "test", "Nuclear test XP")
                if success:
                    st.success("✅ Simple XP system works!")
                    
                    # Show XP data
                    xp_data = simple_engine.get_user_xp(username)
                    st.json(xp_data)
                else:
                    st.error("❌ Even simple XP failed")
    
    # ═══ DATABASE INSPECTION ═══
    with st.expander("🔍 Database Inspection"):
        try:
            with get_db_connection() as conn:
                # Check what tables exist
                tables = conn.execute("SHOW TABLES").fetchall()
                st.markdown("**Available Tables:**")
                for table in tables:
                    st.markdown(f"• {table[0]}")
                
                # Check XP tables specifically
                xp_tables = [t[0] for t in tables if 'xp' in t[0].lower() or 'challenge' in t[0].lower()]
                
                if xp_tables:
                    st.markdown("**XP-Related Tables:**")
                    for table in xp_tables:
                        try:
                            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                            st.markdown(f"• {table}: {count} rows")
                        except:
                            st.markdown(f"• {table}: Error reading")
                else:
                    st.warning("⚠️ No XP tables found - XP system not initialized")
                
                # Show user's XP data if it exists
                try:
                    xp_data = conn.execute("""
                        SELECT COUNT(*) as transactions, SUM(xp_points) as total_xp 
                        FROM xp_transactions 
                        WHERE user_name = ?
                    """, [username]).fetchone()
                    
                    if xp_data and xp_data[0] > 0:
                        st.success(f"✅ Found {xp_data[0]} XP transactions totaling {xp_data[1]} XP")
                    else:
                        st.info("📝 No XP transactions found for this user")
                        
                except Exception as e:
                    st.error(f"❌ Error checking XP data: {e}")
                    
        except Exception as e:
            st.error(f"❌ Database connection error: {e}")
    
    # ═══ FORCE USE SIMPLE SYSTEM ═══
    st.markdown("---")
    st.markdown("### 🚀 Force Simple XP System")
    st.markdown("If complex XP system isn't working, use this to switch to simple mode:")
    
    if st.button("🔄 Use Simple XP System", key="force_simple_xp"):
        st.session_state['use_simple_xp'] = True
        st.success("✅ Switched to Simple XP System! Refresh page to see changes.")
        st.info("💡 Your dashboard will now use the simple, reliable XP system.")

# ═══ CONDITIONAL XP SYSTEM USAGE ═══
# Add this right after your gamification_data calculation:

# CHANGED: Check if we should use simple XP system
if st.session_state.get('use_simple_xp', False):
    st.info("🔧 Using Simple XP System (Developer Mode)")
    gamification_data = get_simple_gamification_data(username)
    
    # Replace daily challenges with simple version
    def render_daily_challenges_simple_wrapper(username, path, current_streaks):
        render_simple_challenges(username, path, current_streaks)
    
    # Override the function for this session
    render_daily_challenges_real = render_daily_challenges_simple_wrapper

# ═══════════════════════════════════════════════════════════════════
# 🛡️ FOOTER & SOVEREIGNTY PHILOSOPHY (FROM YOUR EXISTING CODE)
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")

# Footer (from your existing code)
total_xp = gamification_data["total_xp"]
current_level = gamification_data["current_level"]
total_achievements = len(earned_achievements)

st.markdown("""
<div style="text-align: center; padding: 20px; color: #6b7280;">
    <p>🛡️ <strong>Sovereignty is the new health plan.</strong></p>
    <p><em>Every choice you make today builds the freedom you'll enjoy tomorrow.</em></p>
    <p style="font-size: 12px; margin-top: 12px;">
        💡 <strong>Level {}</strong> • <strong>{:,} XP</strong> • <strong>{} Achievements</strong>
    </p>
</div>
""".format(current_level, total_xp, total_achievements), unsafe_allow_html=True)

# Session state cleanup for next visit
if st.sidebar.button("🚪 Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.success("👋 Logged out successfully!")
    st.info("🔄 Please refresh the page to log in again.")