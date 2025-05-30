import streamlit as st

st.set_page_config(
    page_title="Sovereignty Dashboard",
    page_icon="🏆",
    layout="wide"
)

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

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

# Custom CSS for sovereignty styling
st.markdown("""
<style>
    .sovereignty-card {
        background: linear-gradient(135deg, #1f2937, #374151);
        border: 2px solid #6366f1;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
    }
    
    .achievement-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        margin: 4px;
        font-weight: bold;
        text-align: center;
    }
    
    .legendary { background: linear-gradient(45deg, #f59e0b, #fbbf24); color: #1f2937; }
    .epic { background: linear-gradient(45deg, #7c3aed, #a78bfa); color: white; }
    .rare { background: linear-gradient(45deg, #3b82f6, #60a5fa); color: white; }
    .common { background: linear-gradient(45deg, #6b7280, #9ca3af); color: white; }
    
    .level-title {
        font-size: 28px;
        font-weight: bold;
        color: #6366f1;
        text-align: center;
        margin: 20px 0;
    }
    
    .streak-counter {
        background: linear-gradient(45deg, #ef4444, #f97316);
        color: white;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin: 8px 0;
    }
    
    .next-achievement {
        background: linear-gradient(135deg, #059669, #10b981);
        color: white;
        padding: 16px;
        border-radius: 8px;
        margin: 8px 0;
    }
    
    .sovereignty-metric {
        text-align: center;
        padding: 20px;
        background: rgba(99, 102, 241, 0.1);
        border-radius: 8px;
        border: 1px solid rgba(99, 102, 241, 0.3);
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

# Initialize achievement engine
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_user_achievements(username):
    """Get user achievements with caching"""
    engine = SovereigntyAchievementEngine()
    return engine.calculate_user_achievements(username)

# Load user achievements
with st.spinner("🔍 Analyzing your sovereignty journey..."):
    achievements_data = get_user_achievements(username)

if "error" in achievements_data:
    st.error(f"❌ Error loading achievements: {achievements_data['error']}")
    st.stop()

# Extract achievement data
sovereignty_level = achievements_data.get("sovereignty_level", {})
earned_achievements = achievements_data.get("achievements_earned", [])
progress_metrics = achievements_data.get("progress_metrics", {})
next_achievements = achievements_data.get("next_achievements", [])
achievement_summary = achievements_data.get("achievement_summary", {})

# ═══════════════════════════════════════════════════════════════════
# 🏆 SOVEREIGNTY LEVEL DISPLAY
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("## 👑 Your Sovereignty Level")

level_col1, level_col2, level_col3 = st.columns([2, 1, 2])

with level_col1:
    st.markdown(f"""
    <div class="level-title">
        {sovereignty_level.get('name', 'Unknown Level')}
    </div>
    """, unsafe_allow_html=True)
    
    # Level progress
    progress_info = sovereignty_level.get("progress_to_next", {})
    if "next_level" in progress_info:
        progress_pct = progress_info.get("overall_progress", 0)
        st.progress(progress_pct / 100)
        st.markdown(f"**Progress to {progress_info['next_level']}:** {progress_pct:.1f}%")
    else:
        st.markdown("🎉 **Maximum level achieved!**")

with level_col2:
    st.markdown(f"""
    <div class="sovereignty-metric">
        <h2 style="margin: 0; color: #6366f1;">{sovereignty_level.get('avg_score', 0):.1f}</h2>
        <p style="margin: 5px 0; color: #9ca3af;">Average Score</p>
    </div>
    """, unsafe_allow_html=True)

with level_col3:
    st.markdown(f"""
    <div class="sovereignty-metric">
        <h2 style="margin: 0; color: #6366f1;">{sovereignty_level.get('total_days', 0)}</h2>
        <p style="margin: 5px 0; color: #9ca3af;">Days Tracked</p>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# 🏅 ACHIEVEMENT SHOWCASE
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("## 🏆 Achievement Showcase")

if earned_achievements:
    # Group achievements by rarity
    by_rarity = {"legendary": [], "epic": [], "rare": [], "common": []}
    for ach in earned_achievements:
        rarity = ach.get("rarity", "common")
        if rarity in by_rarity:
            by_rarity[rarity].append(ach)
    
    # Display achievements by rarity
    for rarity in ["legendary", "epic", "rare", "common"]:
        achievements = by_rarity[rarity]
        if achievements:
            rarity_emoji = {"legendary": "🌟", "epic": "💜", "rare": "💙", "common": "🔘"}
            st.markdown(f"### {rarity_emoji[rarity]} {rarity.title()} Achievements ({len(achievements)})")
            
            # Create columns for achievements
            ach_cols = st.columns(min(len(achievements), 3))
            for i, achievement in enumerate(achievements):
                col_idx = i % 3
                with ach_cols[col_idx]:
                    st.markdown(f"""
                    <div class="achievement-badge {rarity}">
                        {achievement['name']}<br>
                        <small>{achievement['description']}</small>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Achievement summary
    summary_col1, summary_col2, summary_col3 = st.columns(3)
    with summary_col1:
        st.metric("🏅 Total Achievements", achievement_summary.get("total", 0))
    with summary_col2:
        legendary_count = achievement_summary.get("by_rarity", {}).get("legendary", 0)
        st.metric("🌟 Legendary", legendary_count)
    with summary_col3:
        epic_count = achievement_summary.get("by_rarity", {}).get("epic", 0)
        st.metric("💜 Epic", epic_count)

else:
    st.info("🎯 Start tracking consistently to earn your first achievements!")

# ═══════════════════════════════════════════════════════════════════
# 🔥 CURRENT STREAKS
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("## 🔥 Active Streaks")

current_streaks = progress_metrics.get("current_streaks", {})
active_streaks = {k: v for k, v in current_streaks.items() if v > 0}

if active_streaks:
    streak_cols = st.columns(min(len(active_streaks), 4))
    for i, (activity, days) in enumerate(active_streaks.items()):
        col_idx = i % 4
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
            <div class="streak-counter">
                {emoji}<br>
                <strong>{days} days</strong><br>
                <small>{activity.replace('_', ' ').title()}</small>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("💡 Start a new streak today! Every sovereignty journey begins with a single step.")

# ═══════════════════════════════════════════════════════════════════
# 🎯 NEXT ACHIEVEMENTS
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("## 🎯 Next Achievements")

if next_achievements:
    for next_ach in next_achievements[:3]:  # Show top 3
        progress_info = next_ach.get("progress", {})
        progress_pct = progress_info.get("progress", 0)
        
        st.markdown(f"""
        <div class="next-achievement">
            <h4 style="margin: 0 0 8px 0;">{next_ach['name']}</h4>
            <p style="margin: 0 0 8px 0; opacity: 0.9;">{next_ach['description']}</p>
            <div style="background: rgba(255,255,255,0.2); border-radius: 10px; height: 8px; margin: 8px 0;">
                <div style="background: #ffffff; height: 8px; border-radius: 10px; width: {progress_pct}%;"></div>
            </div>
            <small>{progress_info.get('message', f'{progress_pct:.0f}% complete')}</small>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("🎉 You're close to earning new achievements! Keep building those sovereignty habits.")

# ═══════════════════════════════════════════════════════════════════
# 📊 SOVEREIGNTY METRICS
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("## 📊 Sovereignty Metrics")

metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)

with metrics_col1:
    sats = progress_metrics.get("total_sats_accumulated", 0)
    st.markdown(f"""
    <div class="sovereignty-metric">
        <h3 style="margin: 0; color: #f59e0b;">₿ {sats:,}</h3>
        <p style="margin: 5px 0; color: #9ca3af;">Sats Stacked</p>
    </div>
    """, unsafe_allow_html=True)

with metrics_col2:
    meals = progress_metrics.get("total_meals_cooked", 0)
    st.markdown(f"""
    <div class="sovereignty-metric">
        <h3 style="margin: 0; color: #10b981;">🍳 {meals}</h3>
        <p style="margin: 5px 0; color: #9ca3af;">Meals Cooked</p>
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
    st.markdown(f"""
    <div class="sovereignty-metric">
        <h3 style="margin: 0; color: #8b5cf6;">📅 {tracking_days}</h3>
        <p style="margin: 5px 0; color: #9ca3af;">Days Tracked</p>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# 📈 PROGRESS CHARTS
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
            
            max_sats = df['cumulative_sats'].max()
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
# 🎯 QUICK ACTIONS
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

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; color: #6b7280;">
    <p>🛡️ <strong>Sovereignty is the new health plan.</strong></p>
    <p><em>Every choice you make today builds the freedom you'll enjoy tomorrow.</em></p>
</div>
""", unsafe_allow_html=True)