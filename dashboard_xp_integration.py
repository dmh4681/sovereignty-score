# Dashboard Integration for Real XP System
# Add these components to your 1_Dashboard.py file

import streamlit as st
from datetime import datetime, date
import uuid

# Import the XP system (add this to your imports section)
from xp_system import XPTransactionEngine, get_gamification_data_real, handle_challenge_completion

# Initialize XP system (add this near the top after your other initializations)
@st.cache_resource
def init_xp_engine():
    """Initialize and cache the XP engine"""
    return XPTransactionEngine()

# Replace your existing gamification metrics calculation with this:
def calculate_gamification_metrics_real(username, achievements_data):
    """Calculate XP using the real transaction system"""
    
    xp_engine = init_xp_engine()
    
    # Get real XP data
    real_xp_data = get_gamification_data_real(xp_engine, username)
    
    # If no real XP data exists yet, fall back to legacy calculation
    if real_xp_data["total_xp"] == 0:
        # Use your existing static calculation as fallback
        legacy_data = calculate_gamification_metrics_legacy(username, achievements_data)
        
        # Optionally migrate legacy XP to new system
        if legacy_data["total_xp"] > 0:
            migrate_legacy_xp(xp_engine, username, legacy_data)
            # Recalculate with migrated data
            real_xp_data = get_gamification_data_real(xp_engine, username)
    
    return real_xp_data

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

# Replace your daily challenges section with this:
def render_daily_challenges_real(username, path, current_streaks):
    """Render daily challenges with real XP integration"""
    
    xp_engine = init_xp_engine()
    
    # Generate today's challenges
    daily_challenges = generate_daily_challenges(username, path, current_streaks)
    
    # Get today's challenge completion status
    challenge_status = xp_engine.get_daily_challenge_status(username)
    completed_challenge_ids = {c["challenge_id"] for c in challenge_status["completed_challenges"] if c["completed"]}
    
    st.markdown("**⚡ Daily Challenges** (Reset at midnight)")
    
    # Add challenge generation date to ensure unique IDs
    today_str = date.today().strftime("%Y%m%d")
    
    challenge_cols = st.columns(3)
    
    for i, challenge in enumerate(daily_challenges):
        with challenge_cols[i]:
            # Create unique challenge ID
            challenge_id = f"{today_str}_{challenge['type']}_{i}"
            
            # Check if this challenge is already completed
            is_completed = challenge_id in completed_challenge_ids
            
            # Use a unique key for each checkbox
            checkbox_key = f"challenge_{challenge_id}_{username}"
            
            # Show completed state or allow completion
            if is_completed:
                st.markdown(f"""
                <div style="background: linear-gradient(45deg, #10b981, #059669); 
                            color: white; padding: 12px; border-radius: 8px; margin: 4px 0;
                            border: 2px solid #047857;">
                    <div style="text-align: center;">
                        <h3 style="margin: 0; font-size: 18px;">{challenge['icon']}</h3>
                        <p style="margin: 4px 0; font-size: 13px; font-weight: bold;">✅ COMPLETED!</p>
                        <p style="margin: 4px 0; font-size: 12px; opacity: 0.9;">{challenge['description']}</p>
                        <p style="margin: 0; font-size: 14px; font-weight: bold;">+{challenge['xp']} XP Earned</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Show when it was completed
                completed_info = next((c for c in challenge_status["completed_challenges"] 
                                     if c["challenge_id"] == challenge_id), None)
                if completed_info and completed_info["completed_at"]:
                    completed_time = datetime.fromisoformat(str(completed_info["completed_at"]))
                    st.markdown(f"<small style='color: #6b7280;'>Completed at {completed_time.strftime('%I:%M %p')}</small>", 
                              unsafe_allow_html=True)
            else:
                # Show completion checkbox
                completed = st.checkbox(f"Mark Complete", key=checkbox_key, value=False)
                
                if completed:
                    # Process the completion
                    challenge_data = {
                        "challenge_id": challenge_id,
                        "challenge_type": challenge['type'],
                        "xp_reward": challenge['xp']
                    }
                    
                    success = handle_challenge_completion(xp_engine, username, challenge_data)
                    
                    if success:
                        st.success(f"🎉 Challenge completed! +{challenge['xp']} XP earned!")
                        st.balloons()
                        
                        # Force refresh to update the display
                        st.rerun()
                    else:
                        st.error("❌ Error completing challenge. Try again.")
                        # Uncheck the box
                        st.session_state[checkbox_key] = False
                
                # Show challenge details
                st.markdown(f"""
                <div style="background: rgba(99, 102, 241, 0.1); 
                            border: 2px solid rgba(99, 102, 241, 0.3); 
                            border-radius: 8px; padding: 12px; margin: 4px 0;">
                    <div style="text-align: center;">
                        <h3 style="margin: 0; font-size: 18px; color: #6366f1;">{challenge['icon']}</h3>
                        <p style="margin: 4px 0; font-size: 13px; color: #374151; font-weight: bold;">{challenge['xp']} XP</p>
                        <p style="margin: 0; font-size: 12px; color: #6b7280;">{challenge['description']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Show today's challenge summary
    if challenge_status["total_completed"] > 0:
        st.success(f"🏆 Completed {challenge_status['total_completed']}/3 challenges today (+{challenge_status['total_xp_earned']} XP)")
    else:
        st.info("💪 Complete challenges to earn XP and level up!")

# Enhanced XP display with real data
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

# Add to your main dashboard after initializing achievements_data:
# Replace this line:
# gamification_data = calculate_gamification_metrics(username, achievements_data)
# With this:
# gamification_data = calculate_gamification_metrics_real(username, achievements_data)

# Then in your daily challenges section, replace with:
# render_daily_challenges_real(username, path, current_streaks)

# And replace your XP display section with:
# render_xp_display_enhanced(gamification_data)

# Optional: Add XP Leaderboard section
def render_xp_leaderboard():
    """Optional leaderboard for competitive users"""
    
    xp_engine = init_xp_engine()
    
    st.markdown("---")
    st.markdown("### 🏆 Sovereignty Leaderboard")
    
    # Timeframe selector
    timeframe = st.selectbox("Timeframe", ["weekly", "monthly", "all_time"], index=0)
    
    # Get leaderboard
    leaderboard = xp_engine.get_xp_leaderboard(limit=10, timeframe=timeframe)
    
    if leaderboard:
        for entry in leaderboard:
            rank_emoji = {"1": "🥇", "2": "🥈", "3": "🥉"}.get(str(entry["rank"]), f"{entry['rank']}.")
            
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; 
                        padding: 8px 12px; margin: 4px 0; background: rgba(99, 102, 241, 0.05); 
                        border-radius: 8px; border-left: 3px solid #6366f1;">
                <span><strong>{rank_emoji}</strong> {entry['username']} (Level {entry['level']})</span>
                <span style="color: #10b981; font-weight: bold;">{entry['total_xp']:,} XP</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("🚀 Be the first to earn XP and claim the top spot!")

# Debug/Admin section (remove in production)
def render_xp_debug_section(username):
    """Debug section for testing XP system"""
    
    with st.expander("🔧 XP System Debug (Dev Only)"):
        st.markdown("**Quick XP Test Actions:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Award Test XP"):
                xp_engine = init_xp_engine()
                success = xp_engine.award_xp(username, 25, "debug", "Test XP award", "debug_001")
                if success:
                    st.success("✅ Awarded 25 test XP!")
                    st.rerun()
        
        with col2:
            if st.button("Complete Test Challenge"):
                xp_engine = init_xp_engine()
                success = xp_engine.complete_daily_challenge(username, f"debug_{datetime.now().strftime('%H%M%S')}", "debug", 30)
                if success:
                    st.success("✅ Completed test challenge!")
                    st.rerun()
        
        with col3:
            if st.button("Reset Today's Challenges"):
                # This would require a reset function in your XP engine
                st.warning("Reset function not implemented yet")
        
        # Show raw XP data
        xp_engine = init_xp_engine()
        raw_data = xp_engine.get_user_total_xp(username)
        st.json(raw_data)