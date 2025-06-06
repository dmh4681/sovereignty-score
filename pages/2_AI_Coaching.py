import streamlit as st
import os
import time
import sys
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
import json
from io import BytesIO
from datetime import datetime, timedelta

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from db import get_db_connection
from sovereignty_achievements import SovereigntyAchievementEngine

# Setup
st.set_page_config(page_title="AI Coaching", page_icon="🧠", layout="wide")
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COACHING_ASSISTANT_ID = "asst_I7akt1W4Je7c5U3cN1guiefc"
client = OpenAI(api_key=OPENAI_API_KEY)

# Enhanced CSS for coaching interface
st.markdown("""
<style>
    .coaching-hero {
        background: linear-gradient(135deg, #1f2937, #374151);
        border: 3px solid #10b981;
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        text-align: center;
        color: white;
    }
    
    .sovereignty-data-card {
        background: rgba(16, 185, 129, 0.1);
        border: 2px solid rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
    }
    
    .coaching-insight {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(99, 102, 241, 0.1));
        border-left: 4px solid #8b5cf6;
        padding: 16px;
        margin: 12px 0;
        border-radius: 0 8px 8px 0;
    }
    
    .achievement-highlight {
        background: linear-gradient(45deg, #f59e0b, #fbbf24);
        color: #1f2937;
        padding: 12px;
        border-radius: 8px;
        margin: 4px 0;
        font-weight: bold;
        text-align: center;
    }
    
    .streak-highlight {
        background: linear-gradient(45deg, #ef4444, #f97316);
        color: white;
        padding: 10px;
        border-radius: 8px;
        margin: 4px 0;
        text-align: center;
    }
    
    .challenge-status {
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 8px;
        padding: 12px;
        margin: 6px 0;
    }
</style>
""", unsafe_allow_html=True)

# Get user info
username = st.session_state.get("username", None)
path = st.session_state.get("path", None)

if not username or not path:
    st.error("Please log in through the main page to access AI Coaching.")
    st.stop()

# Enhanced header with sovereignty branding
st.markdown(f"""
<div class="coaching-hero">
    <h1>🧠 Sovereignty AI Coach</h1>
    <h3>Consciousness evolution through practical action</h3>
    <p style="margin: 8px 0; opacity: 0.9;">Personalized coaching based on your complete sovereignty journey</p>
    <p style="margin: 0; font-size: 14px; opacity: 0.7;">Path: {path.replace('_', ' ').title()} • User: {username}</p>
</div>
""", unsafe_allow_html=True)

# Load comprehensive user data for coaching
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_comprehensive_user_data(username):
    """Load all user data for enhanced AI coaching"""
    try:
        # Get achievement data
        engine = SovereigntyAchievementEngine()
        achievements_data = engine.calculate_user_achievements(username)
        
        # Get recent tracking data
        with get_db_connection() as conn:
            # Last 30 days of tracking
            recent_data = conn.execute("""
                SELECT timestamp, score, home_cooked_meals, junk_food, exercise_minutes,
                       strength_training, no_spending, invested_bitcoin, btc_usd, btc_sats,
                       meditation, gratitude, read_or_learned, environmental_action
                FROM sovereignty 
                WHERE username = ? AND timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT 30
            """, [username, datetime.now() - timedelta(days=30)]).fetchall()
            
            # All-time summary
            all_time_data = conn.execute("""
                SELECT COUNT(*) as total_days,
                       AVG(score) as avg_score,
                       MAX(score) as best_score,
                       MIN(score) as worst_score,
                       SUM(btc_sats) as total_sats,
                       SUM(home_cooked_meals) as total_meals,
                       SUM(CASE WHEN meditation = 1 THEN 1 ELSE 0 END) as meditation_days,
                       SUM(CASE WHEN strength_training = 1 THEN 1 ELSE 0 END) as strength_days
                FROM sovereignty 
                WHERE username = ?
            """, [username]).fetchone()
        
        return {
            "achievements": achievements_data,
            "recent_tracking": recent_data,
            "all_time_stats": all_time_data,
            "loaded_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        st.error(f"Error loading user data: {e}")
        return None

# Load user data
with st.spinner("🔍 Analyzing your complete sovereignty journey..."):
    user_data = load_comprehensive_user_data(username)

if not user_data or "error" in user_data.get("achievements", {}):
    st.error("❌ Unable to load your sovereignty data. Please ensure you have tracking history.")
    st.stop()

# Extract key insights for coaching
achievements = user_data["achievements"]
recent_tracking = user_data["recent_tracking"]
all_time_stats = user_data["all_time_stats"]

sovereignty_level = achievements.get("sovereignty_level", {})
earned_achievements = achievements.get("achievements_earned", [])
progress_metrics = achievements.get("progress_metrics", {})
next_achievements = achievements.get("next_achievements", [])

# Display user sovereignty profile for transparency
if st.sidebar.button("🔄 Reset Session"):
    st.session_state.pop("coaching_thread_id", None)
    st.session_state.pop("coaching_messages", None)
    st.session_state.pop("coaching_started", None)
    st.session_state.pop("developmental_stage", None)
    st.rerun()

# Sidebar: Sovereignty Profile Summary
st.sidebar.markdown("### 🛡️ Your Sovereignty Profile")
st.sidebar.markdown(f"**Level:** {sovereignty_level.get('name', 'Unknown')}")
st.sidebar.markdown(f"**Avg Score:** {sovereignty_level.get('avg_score', 0):.1f}")
st.sidebar.markdown(f"**Total Days:** {sovereignty_level.get('total_days', 0)}")
st.sidebar.markdown(f"**Achievements:** {len(earned_achievements)}")

# Show current streaks
current_streaks = progress_metrics.get("current_streaks", {})
active_streaks = {k: v for k, v in current_streaks.items() if v > 0}

if active_streaks:
    st.sidebar.markdown("### 🔥 Active Streaks")
    for activity, days in list(active_streaks.items())[:3]:
        emoji = {"meditation": "🧘‍♂️", "strength_training": "💪", "invested_bitcoin": "₿", 
                "gratitude": "🙏", "environmental_action": "🌍"}.get(activity, "⚡")
        st.sidebar.markdown(f"{emoji} **{days}** {activity.replace('_', ' ').title()}")

# Show recent performance
if recent_tracking:
    recent_scores = [row[1] for row in recent_tracking if row[1] is not None]
    if recent_scores:
        recent_avg = sum(recent_scores) / len(recent_scores)
        st.sidebar.markdown(f"### 📈 Recent Performance")
        st.sidebar.markdown(f"**Last 7 days avg:** {recent_avg:.1f}")
        
        # Performance trend
        if len(recent_scores) >= 7:
            early_week = sum(recent_scores[:3]) / 3
            late_week = sum(recent_scores[-3:]) / 3
            trend = "📈 Improving" if late_week > early_week else "📉 Declining" if late_week < early_week else "➡️ Stable"
            st.sidebar.markdown(f"**Trend:** {trend}")

# Enhanced tracker renderer with sovereignty insights
def render_enhanced_tracker_from_reply(reply, user_insights):
    if "```json" not in reply:
        return

    try:
        json_str = reply.split("```json")[1].split("```")[0].strip()
        tracker_data = json.loads(json_str)

        st.markdown("---")
        st.markdown("### 📋 Personalized Sovereignty Tracker")
        
        # Show how this tracker addresses their specific profile
        st.markdown(f"""
        <div class="coaching-insight">
            <h4>🎯 Designed for Your Journey</h4>
            <p><strong>Your Level:</strong> {sovereignty_level.get('name', 'Unknown')}</p>
            <p><strong>Focus Area:</strong> {tracker_data.get('focus_area', 'General Development')}</p>
            <p><strong>Personalization:</strong> Based on your {len(earned_achievements)} achievements and current {sovereignty_level.get('avg_score', 0):.0f} avg score</p>
        </div>
        """, unsafe_allow_html=True)

        # Enhanced tracker display
        df = pd.DataFrame({
            "Day": tracker_data["days"],
            "Morning Habit": [tracker_data["morning_habit"]] * 7,
            "Evening Habit": [tracker_data["evening_habit"]] * 7
        })

        st.table(df)

        # Show goals with sovereignty context
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🎯 Weekly Goals**")
            for goal in tracker_data["weekly_goals"]:
                st.markdown(f"- {goal}")
        
        with col2:
            st.markdown("**🔥 Streak Targets**")
            if active_streaks:
                st.markdown("*Build on your current streaks:*")
                for activity, days in list(active_streaks.items())[:3]:
                    st.markdown(f"- {activity.replace('_', ' ').title()}: {days} → {days + 7} days")
            else:
                st.markdown("*Start your first 7-day streaks:*")
                st.markdown("- Choose 2-3 activities to focus on")

        # Sovereignty reminder with personal context
        st.markdown(f"""
        <div class="achievement-highlight">
            🛡️ Sovereignty Reminder: {tracker_data['sovereign_reminder']}
        </div>
        """, unsafe_allow_html=True)

        # Enhanced download with user data
        buffer = BytesIO()
        
        # Add user profile sheet
        profile_data = {
            "Metric": ["Username", "Path", "Level", "Avg Score", "Total Days", "Achievements", "Active Streaks"],
            "Value": [
                username,
                path.replace('_', ' ').title(),
                sovereignty_level.get('name', 'Unknown'),
                f"{sovereignty_level.get('avg_score', 0):.1f}",
                sovereignty_level.get('total_days', 0),
                len(earned_achievements),
                len(active_streaks)
            ]
        }
        
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            # Main tracker
            df.to_excel(writer, index=False, sheet_name="Weekly Tracker")
            
            # User profile
            pd.DataFrame(profile_data).to_excel(writer, index=False, sheet_name="Your Profile")
            
            # Goals and wisdom
            pd.DataFrame({"Weekly Goals": tracker_data["weekly_goals"]}).to_excel(writer, index=False, sheet_name="Goals")
            pd.DataFrame({"Sovereignty Wisdom": [tracker_data["sovereign_reminder"]]}).to_excel(writer, index=False, sheet_name="Philosophy")
            
            # Current streaks (if any)
            if active_streaks:
                streak_data = pd.DataFrame([
                    {"Activity": k.replace('_', ' ').title(), "Current Days": v, "Target": v + 7} 
                    for k, v in active_streaks.items()
                ])
                streak_data.to_excel(writer, index=False, sheet_name="Current Streaks")

        buffer.seek(0)

        st.download_button(
            label="📥 Download Personalized Sovereignty Tracker",
            data=buffer,
            file_name=f"sovereignty_tracker_{username}_{tracker_data.get('focus_area', 'general').lower().replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error("⚠️ Failed to generate enhanced tracker.")
        st.exception(e)

# Thread & message history
if "coaching_thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.coaching_thread_id = thread.id
    st.session_state.coaching_messages = []

# Enhanced intake form with sovereignty context
if "coaching_started" not in st.session_state:
    
    # Show sovereignty insights before coaching
    st.markdown("### 🔍 Your Sovereignty Journey Analysis")
    
    insights_col1, insights_col2, insights_col3 = st.columns(3)
    
    with insights_col1:
        st.markdown("""
        <div class="sovereignty-data-card">
            <h4>🏆 Achievement Status</h4>
            <p><strong>Level:</strong> {}</p>
            <p><strong>Earned:</strong> {}</p>
            <p><strong>Next Goal:</strong> {}</p>
        </div>
        """.format(
            sovereignty_level.get('name', 'Unknown'),
            len(earned_achievements),
            next_achievements[0]['name'] if next_achievements else 'Keep building!'
        ), unsafe_allow_html=True)
    
    with insights_col2:
        total_sats = progress_metrics.get("total_sats_accumulated", 0)
        total_meals = progress_metrics.get("total_meals_cooked", 0)
        
        st.markdown(f"""
        <div class="sovereignty-data-card">
            <h4>📊 Key Metrics</h4>
            <p><strong>Sats Stacked:</strong> {total_sats:,}</p>
            <p><strong>Meals Cooked:</strong> {total_meals}</p>
            <p><strong>Tracking Days:</strong> {sovereignty_level.get('total_days', 0)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with insights_col3:
        if active_streaks:
            top_streak = max(active_streaks.items(), key=lambda x: x[1])
            st.markdown(f"""
            <div class="sovereignty-data-card">
                <h4>🔥 Streak Power</h4>
                <p><strong>Best:</strong> {top_streak[1]} days</p>
                <p><strong>Activity:</strong> {top_streak[0].replace('_', ' ').title()}</p>
                <p><strong>Active:</strong> {len(active_streaks)} streaks</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="sovereignty-data-card">
                <h4>💡 Opportunity</h4>
                <p><strong>Streaks:</strong> None active</p>
                <p><strong>Potential:</strong> High</p>
                <p><strong>Focus:</strong> Consistency</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    with st.form("enhanced_coaching_form"):
        st.subheader("🎯 What would you like coaching on?")
        
        # Core challenge/goal with sovereignty context
        focus_area = st.selectbox("Select your focus area", [
            "Physical Health & Body Sovereignty", 
            "Mental Wellbeing & Cognitive Freedom", 
            "Financial Growth & Economic Independence", 
            "Environmental Impact & Planetary Stewardship", 
            "Spiritual Development & Consciousness Evolution",
            "Overall Sovereignty Integration"
        ])
        
        challenge = st.text_area(
            "Describe your current challenge or goal", 
            placeholder="I'm struggling with... or I want to achieve...",
            help="Be specific about what you're experiencing in your sovereignty journey"
        )
        
        # Time and consistency factors
        time_commitment = st.selectbox("How much time can you commit daily?", [
            "5-15 minutes", "15-30 minutes", "30-60 minutes", "1-2 hours", "2+ hours"])
        
        obstacle = st.selectbox("What tends to derail your consistency?", [
            "Lack of time", "Low motivation", "Mental distraction", "Overwhelm", 
            "Lack of clarity", "Social pressure", "System resistance", "Other"])
        
        # Sovereignty-specific questions
        st.markdown("---")
        st.markdown("**🛡️ Sovereignty-Specific Context:**")
        
        sovereignty_priority = st.selectbox("Which aspect of sovereignty feels most urgent?", [
            "Building anti-fragile daily routines",
            "Breaking free from limiting patterns", 
            "Developing financial independence",
            "Strengthening physical resilience",
            "Expanding consciousness and awareness",
            "Creating systemic change in my environment"
        ])
        
        current_obstacles = st.multiselect("What systems or patterns are you working to exit?", [
            "Processed food dependency", "Consumer debt cycles", "Screen addiction", 
            "Stress and overwhelm", "Social conformity pressure", "Scarcity mindset",
            "Victim consciousness", "External validation seeking", "Other"
        ])
        
        # Developmental stage indicators (enhanced with sovereignty lens)
        st.markdown("---")
        st.markdown("**🧠 Help us understand your approach:**")
        
        success_metric = st.selectbox("What does sovereignty success look like to you?", [
            "Clear metrics, measurable progress, and optimized performance",
            "Feeling aligned and balanced across all life domains", 
            "Contributing to collective awakening and systemic change",
            "Transcending conventional categories through integral practice"
        ])
        
        motivation_style = st.selectbox("What motivates your sovereignty journey?", [
            "Personal achievement, optimization, and competitive excellence",
            "Harmony with nature, community healing, and collective wellbeing",
            "Understanding complex systems and creating adaptive solutions",
            "Serving the evolution of consciousness and planetary transformation"
        ])
        
        complexity_comfort = st.selectbox("How do you prefer to approach sovereignty challenges?", [
            "Clear methodologies, proven systems, and step-by-step progression",
            "Holistic approaches that honor multiple perspectives and values",
            "Dynamic strategies that adapt to changing conditions and feedback",
            "Paradoxical solutions that transcend either/or thinking patterns"
        ])
        
        # Context and deeper purpose
        st.markdown("---")
        context = st.text_area(
            "Any additional context about your sovereignty journey?", 
            placeholder="Share relevant details about your situation, constraints, or what you've already tried..."
        )
        
        why_now = st.text_area(
            "Why do you want to develop this area of sovereignty now?", 
            placeholder="What's driving this focus at this point in your journey?"
        )
        
        sovereign_vision = st.text_area(
            "If this challenge was resolved, what would that unlock for your sovereignty?", 
            placeholder="Describe your desired future state and what becomes possible..."
        )
        
        submitted = st.form_submit_button("🚀 Get Personalized Sovereignty Coaching")

    if submitted:
        st.info("🤖 AI Coach is analyzing your complete sovereignty profile...")

        # Enhanced developmental stage mapping
        stage_indicators = {
            "Orange": [
                "Clear metrics, measurable progress, and optimized performance",
                "Personal achievement, optimization, and competitive excellence", 
                "Clear methodologies, proven systems, and step-by-step progression"
            ],
            "Green": [
                "Feeling aligned and balanced across all life domains",
                "Harmony with nature, community healing, and collective wellbeing",
                "Holistic approaches that honor multiple perspectives and values"
            ],
            "Teal": [
                "Contributing to collective awakening and systemic change",
                "Understanding complex systems and creating adaptive solutions",
                "Dynamic strategies that adapt to changing conditions and feedback"
            ],
            "Turquoise": [
                "Transcending conventional categories through integral practice",
                "Serving the evolution of consciousness and planetary transformation",
                "Paradoxical solutions that transcend either/or thinking patterns"
            ]
        }
        
        # Determine developmental center of gravity
        user_responses = [success_metric, motivation_style, complexity_comfort]
        stage_scores = {stage: 0 for stage in stage_indicators.keys()}
        
        for response in user_responses:
            for stage, indicators in stage_indicators.items():
                if response in indicators:
                    stage_scores[stage] += 1
        
        likely_stage = max(stage_scores, key=stage_scores.get)
        st.session_state.developmental_stage = likely_stage
        
        # Enhanced user prompt with complete sovereignty data
        comprehensive_prompt = f"""
        You are an elite Sovereignty Coach who integrates consciousness evolution with practical action. You have access to this user's complete sovereignty journey data and must provide coaching that's precisely calibrated to their current state and developmental capacity.

        USER SOVEREIGNTY PROFILE:
        Username: {username}
        Sovereignty Path: {path.replace('_',' ')}
        Current Level: {sovereignty_level.get('name', 'Unknown')}
        Average Score: {sovereignty_level.get('avg_score', 0):.1f}/100
        Total Tracking Days: {sovereignty_level.get('total_days', 0)}
        Developmental Complexity: {likely_stage} consciousness
        
        ACHIEVEMENT DATA:
        Total Achievements: {len(earned_achievements)}
        Recent Achievements: {[a['name'] for a in earned_achievements[-3:]] if earned_achievements else 'None yet'}
        Next Milestone: {next_achievements[0]['name'] if next_achievements else 'Continue building foundation'}
        
        CURRENT PERFORMANCE:
        Active Streaks: {dict(list(active_streaks.items())[:5]) if active_streaks else 'None active'}
        Recent Avg Score: {sum([row[1] for row in recent_tracking[:7] if row[1]]) / len([row[1] for row in recent_tracking[:7] if row[1]]) if recent_tracking and any(row[1] for row in recent_tracking[:7]) else 'No recent data'}
        Total Sats Stacked: {progress_metrics.get('total_sats_accumulated', 0):,}
        Total Meals Cooked: {progress_metrics.get('total_meals_cooked', 0)}
        
        PATH-SPECIFIC PERFORMANCE:
        Based on {path} path, their current habits show:
        - Meditation days: {sum(1 for row in recent_tracking if row[10]) if recent_tracking else 0}/30 recent
        - Strength training: {sum(1 for row in recent_tracking if row[5]) if recent_tracking else 0}/30 recent  
        - Bitcoin investing: {sum(1 for row in recent_tracking if row[7]) if recent_tracking else 0}/30 recent
        - Home cooking: {sum(row[2] for row in recent_tracking if row[2]) if recent_tracking else 0} meals in 30 days
        
        COACHING REQUEST:
        Focus Area: {focus_area}
        Current Challenge: {challenge}
        Time Available: {time_commitment}
        Main Obstacle: {obstacle}
        Sovereignty Priority: {sovereignty_priority}
        Systems to Exit: {current_obstacles}
        Why Now: {why_now}
        Vision: {sovereign_vision}
        Context: {context}
        
        Success Definition: {success_metric}
        Motivation Style: {motivation_style}
        Complexity Comfort: {complexity_comfort}

        COACHING REQUIREMENTS:
        1. PERSONALIZATION: Reference their specific achievements, streaks, and performance data
        2. DEVELOPMENTAL CALIBRATION: Match language and approach to {likely_stage} consciousness level
        3. PATH ALIGNMENT: Provide guidance aligned with their {path} sovereignty path
        4. PRACTICAL INTEGRATION: Connect insights to their actual habit patterns and current challenges
        5. ACHIEVEMENT AWARENESS: Acknowledge their current level while pointing toward next milestones
        6. STREAK CONSCIOUSNESS: Address their active streaks and opportunities for consistency
        7. SOVEREIGNTY FOCUS: Keep everything tied to personal sovereignty and freedom principles

        Respond with powerful, personalized coaching that shows you understand exactly where they are in their sovereignty journey and provides specific, actionable guidance for their next level of development.
        """

        client.beta.threads.messages.create(
            thread_id=st.session_state.coaching_thread_id,
            role="user",
            content=comprehensive_prompt
        )

        run = client.beta.threads.runs.create(
            thread_id=st.session_state.coaching_thread_id,
            assistant_id=COACHING_ASSISTANT_ID
        )

        while True:
            run = client.beta.threads.runs.retrieve(thread_id=st.session_state.coaching_thread_id, run_id=run.id)
            if run.status == "completed":
                break
            time.sleep(1)

        messages = client.beta.threads.messages.list(thread_id=st.session_state.coaching_thread_id)
        reply = messages.data[0].content[0].text.value
        st.session_state.coaching_messages.append({"role": "assistant", "content": reply})
        st.session_state.coaching_started = True

        with st.chat_message("assistant"):
            st.markdown(reply)
            render_enhanced_tracker_from_reply(reply, user_data)

# Enhanced follow-up conversation with sovereignty awareness
if st.session_state.get("coaching_started"):
    st.markdown("---")
    st.subheader("🗣️ Continue Your Sovereignty Coaching Session")
    
    # Enhanced sidebar with coaching context
    if "developmental_stage" in st.session_state:
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"### 🧠 Coaching Profile")
        st.sidebar.markdown(f"**Stage:** {st.session_state.developmental_stage}")
        stage_descriptions = {
            "Orange": "Achievement-focused, metrics-driven",
            "Green": "Community-oriented, holistically-minded", 
            "Teal": "Systems-thinking, complexity-comfortable",
            "Turquoise": "Transpersonal, evolution-focused"
        }
        st.sidebar.markdown(f"*{stage_descriptions.get(st.session_state.developmental_stage, 'Integral approach')}*")

    # Show conversation history with enhanced rendering
    for msg in st.session_state.coaching_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                render_enhanced_tracker_from_reply(msg["content"], user_data)

    # Replace the chat input section in your 2_AI_Coaching.py file
# Find this section around line 620-650 and replace it with:

# Enhanced follow-up input with suggestions
st.markdown("**💡 Suggested follow-up questions:**")

suggestion_cols = st.columns(3)

with suggestion_cols[0]:
    if st.button("🎯 Optimize my current streaks", key="optimize_streaks"):
        follow_up = f"How can I optimize my current streaks: {', '.join([f'{k} ({v} days)' for k, v in active_streaks.items()])}?"
        st.session_state['pending_question'] = follow_up
        st.rerun()

with suggestion_cols[1]:
    if st.button("📈 Improve my weak areas", key="improve_weak"):
        follow_up = "What are my biggest sovereignty weak spots based on my data, and how should I address them?"
        st.session_state['pending_question'] = follow_up
        st.rerun()

with suggestion_cols[2]:
    if st.button("🏆 Next achievement strategy", key="next_achievement"):
        next_ach = next_achievements[0]['name'] if next_achievements else "next milestone"
        follow_up = f"What's the best strategy to achieve my next milestone: {next_ach}?"
        st.session_state['pending_question'] = follow_up
        st.rerun()

# Handle pending question from button clicks
if 'pending_question' in st.session_state:
    follow_up = st.session_state['pending_question']
    del st.session_state['pending_question']
    
    # Process the suggested question
    with st.chat_message("user"):
        st.markdown(follow_up)

    st.session_state.coaching_messages.append({"role": "user", "content": follow_up})

    # Enhanced follow-up with current state awareness
    enhanced_follow_up = f"""
    Continue coaching this user based on their complete sovereignty profile.
    
    CURRENT STATE REMINDER:
    - Level: {sovereignty_level.get('name', 'Unknown')} ({sovereignty_level.get('avg_score', 0):.1f} avg score)
    - Active Streaks: {active_streaks}
    - Path: {path} 
    - Developmental Stage: {st.session_state.get('developmental_stage', 'Orange')}
    - Total Achievements: {len(earned_achievements)}
    
    User follow-up: {follow_up}
    
    Maintain appropriate developmental language and provide coaching that builds on their specific sovereignty data. Reference their actual patterns and achievements when relevant.
    """

    client.beta.threads.messages.create(
        thread_id=st.session_state.coaching_thread_id,
        role="user",
        content=enhanced_follow_up
    )

    run = client.beta.threads.runs.create(
        thread_id=st.session_state.coaching_thread_id,
        assistant_id=COACHING_ASSISTANT_ID
    )

    with st.spinner("🧠 Integrating your sovereignty data..."):
        while True:
            run = client.beta.threads.runs.retrieve(thread_id=st.session_state.coaching_thread_id, run_id=run.id)
            if run.status == "completed":
                break
            time.sleep(1)

    messages = client.beta.threads.messages.list(thread_id=st.session_state.coaching_thread_id)
    reply = messages.data[0].content[0].text.value

    with st.chat_message("assistant"):
        st.markdown(reply)
        render_enhanced_tracker_from_reply(reply, user_data)

    st.session_state.coaching_messages.append({"role": "assistant", "content": reply})

# Regular chat input for manual questions
follow_up = st.chat_input("Continue the coaching conversation...")

if follow_up:
    with st.chat_message("user"):
        st.markdown(follow_up)

    st.session_state.coaching_messages.append({"role": "user", "content": follow_up})

    # Enhanced follow-up with current state awareness
    enhanced_follow_up = f"""
    Continue coaching this user based on their complete sovereignty profile.
    
    CURRENT STATE REMINDER:
    - Level: {sovereignty_level.get('name', 'Unknown')} ({sovereignty_level.get('avg_score', 0):.1f} avg score)
    - Active Streaks: {active_streaks}
    - Path: {path} 
    - Developmental Stage: {st.session_state.get('developmental_stage', 'Orange')}
    - Total Achievements: {len(earned_achievements)}
    
    User follow-up: {follow_up}
    
    Maintain appropriate developmental language and provide coaching that builds on their specific sovereignty data. Reference their actual patterns and achievements when relevant.
    """

    client.beta.threads.messages.create(
        thread_id=st.session_state.coaching_thread_id,
        role="user",
        content=enhanced_follow_up
    )

    run = client.beta.threads.runs.create(
        thread_id=st.session_state.coaching_thread_id,
        assistant_id=COACHING_ASSISTANT_ID
    )

    with st.spinner("🧠 Integrating your sovereignty data..."):
        while True:
            run = client.beta.threads.runs.retrieve(thread_id=st.session_state.coaching_thread_id, run_id=run.id)
            if run.status == "completed":
                break
            time.sleep(1)

    messages = client.beta.threads.messages.list(thread_id=st.session_state.coaching_thread_id)
    reply = messages.data[0].content[0].text.value

    with st.chat_message("assistant"):
        st.markdown(reply)
        render_enhanced_tracker_from_reply(reply, user_data)

    st.session_state.coaching_messages.append({"role": "assistant", "content": reply})

# Footer with sovereignty motivation
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; color: #6b7280;">
    <p>🛡️ <strong>Your sovereignty journey is unique and powerful.</strong></p>
    <p><em>Every coaching insight builds your capacity for true freedom.</em></p>
    <p style="font-size: 12px; margin-top: 12px;">
        Level {level} • {total_achievements} Achievements • {active_streak_count} Active Streaks
    </p>
</div>
""".format(
    level=sovereignty_level.get('name', 'Unknown'),
    total_achievements=len(earned_achievements),
    active_streak_count=len(active_streaks)
), unsafe_allow_html=True)