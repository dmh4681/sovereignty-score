import streamlit as st
import os
import time
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
import json
from io import BytesIO

# Setup
st.set_page_config(page_title="AI Coaching", page_icon="🧠", layout="wide")
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COACHING_ASSISTANT_ID = "asst_I7akt1W4Je7c5U3cN1guiefc"
client = OpenAI(api_key=OPENAI_API_KEY)

# Get user info
username = st.session_state.get("username", None)
path = st.session_state.get("path", None)

if not username or not path:
    st.error("Please log in through the main page to access AI Coaching.")
    st.stop()

st.title("🧠 Sovereignty AI Coach")
st.markdown("*Consciousness evolution through practical action*")
st.sidebar.markdown(f"### Logged in as {username}")
st.sidebar.markdown(f"### Path: {path.replace('_',' ').title()}")

if st.sidebar.button("🔄 Reset Session"):
    st.session_state.pop("coaching_thread_id", None)
    st.session_state.pop("coaching_messages", None)
    st.session_state.pop("coaching_started", None)
    st.session_state.pop("developmental_stage", None)
    st.rerun()

# Enhanced tracker renderer with more sophistication
def render_tracker_from_reply(reply):
    if "```json" not in reply:
        return

    try:
        json_str = reply.split("```json")[1].split("```")[0].strip()
        tracker_data = json.loads(json_str)

        df = pd.DataFrame({
            "Day": tracker_data["days"],
            "Morning Habit": [tracker_data["morning_habit"]] * 7,
            "Evening Habit": [tracker_data["evening_habit"]] * 7
        })

        st.subheader("📋 Sovereign Tracker Preview")
        st.table(df)

        st.markdown("**🎯 Weekly Goals**")
        for goal in tracker_data["weekly_goals"]:
            st.markdown(f"- {goal}")

        st.markdown(f"🧠 *{tracker_data['sovereign_reminder']}*")

        # Enhanced download with better formatting
        buffer = BytesIO()
        df = df.copy()

        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Sovereign Tracker")
            
            # Add goals and reminder to separate sheets
            goals_df = pd.DataFrame({"Weekly Goals": tracker_data["weekly_goals"]})
            goals_df.to_excel(writer, index=False, sheet_name="Goals")
            
            reminder_df = pd.DataFrame({"Sovereign Reminder": [tracker_data["sovereign_reminder"]]})
            reminder_df.to_excel(writer, index=False, sheet_name="Philosophy")

        buffer.seek(0)

        st.download_button(
            label="📥 Download Complete Tracker as Excel",
            data=buffer,
            file_name=f"sovereign_tracker_{username}_{tracker_data.get('focus_area', 'general')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error("⚠️ Failed to parse tracker output.")
        st.exception(e)

# Thread & message history
if "coaching_thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.coaching_thread_id = thread.id
    st.session_state.coaching_messages = []

# Step 1: Enhanced intake form with developmental assessment
if "coaching_started" not in st.session_state:

    with st.form("coaching_form"):
        st.subheader("🎯 What would you like coaching on?")
        
        # Core challenge/goal
        focus_area = st.selectbox("Select your focus area", [
            "Physical Health", "Mental Wellbeing", "Financial Growth", "Environmental Impact", "Spiritual Development"])
        challenge = st.text_area("Describe your current challenge or goal", placeholder="I'm struggling with... or I want to achieve...")
        
        # Practical constraints
        time_commitment = st.selectbox("How much time can you commit daily?", [
            "5-15 minutes", "15-30 minutes", "30-60 minutes", "1-2 hours", "2+ hours"])
        obstacle = st.selectbox("What tends to derail your consistency?", [
            "Lack of time", "Low motivation", "Mental distraction", "Overwhelm", "Lack of clarity", "Other"])
        
        # Developmental stage indicators (subtle assessment)
        st.markdown("---")
        st.markdown("**🧠 Help us understand your approach:**")
        
        success_metric = st.selectbox("What does success look like to you?", [
            "Clear metrics and measurable progress",
            "Feeling aligned and balanced across life areas", 
            "Contributing to something bigger than myself",
            "Creating systemic change that serves the whole"
        ])
        
        motivation_style = st.selectbox("What motivates you most?", [
            "Personal achievement and optimization",
            "Harmony with nature and community",
            "Understanding complex interconnections",
            "Serving collective awakening and evolution"
        ])
        
        complexity_comfort = st.selectbox("How do you prefer to approach challenges?", [
            "Clear steps and proven methodologies",
            "Holistic approaches that honor multiple perspectives",
            "Dynamic strategies that adapt to changing conditions",
            "Paradoxical solutions that transcend either/or thinking"
        ])
        
        # Context and deeper purpose
        st.markdown("---")
        context = st.text_area("Any additional context (optional)", placeholder="Share any relevant details about your situation, preferences, or constraints...")
        why_now = st.text_area("Why do you want to improve this now?", placeholder="What's driving this shift at this point in your life?")
        sovereign_goal = st.text_area("If this challenge was resolved, what would that unlock for you?", placeholder="Describe your desired future state...")
        
        submitted = st.form_submit_button("🚀 Get AI Coaching")

    if submitted:
        st.info("🤖 AI Coach is analyzing your developmental profile...")

        # Map responses to developmental stages
        stage_indicators = {
            "Orange": ["Clear metrics and measurable progress", "Personal achievement and optimization", "Clear steps and proven methodologies"],
            "Green": ["Feeling aligned and balanced across life areas", "Harmony with nature and community", "Holistic approaches that honor multiple perspectives"],
            "Teal": ["Creating systemic change that serves the whole", "Understanding complex interconnections", "Dynamic strategies that adapt to changing conditions"],
            "Turquoise": ["Contributing to something bigger than myself", "Serving collective awakening and evolution", "Paradoxical solutions that transcend either/or thinking"]
        }
        
        # Determine likely developmental center of gravity
        user_responses = [success_metric, motivation_style, complexity_comfort]
        stage_scores = {stage: 0 for stage in stage_indicators.keys()}
        
        for response in user_responses:
            for stage, indicators in stage_indicators.items():
                if response in indicators:
                    stage_scores[stage] += 1
        
        likely_stage = max(stage_scores, key=stage_scores.get)
        st.session_state.developmental_stage = likely_stage
        
        # Enhanced user prompt with Wilber integration
        user_prompt = f"""
        You are a Sovereignty Coach trained in Ken Wilber's Integral Theory and AQAL framework. You understand that personal sovereignty is consciousness evolution in action.

        USER PROFILE:
        Username: {username}
        Sovereignty Path: {path.replace('_',' ')}
        Developmental Stage: {likely_stage} (based on assessment)
        
        COACHING REQUEST:
        Focus Area: {focus_area}
        Challenge: {challenge}
        Time Commitment: {time_commitment}
        Success Definition: {success_metric}
        Motivation Style: {motivation_style}
        Complexity Comfort: {complexity_comfort}
        Key Obstacle: {obstacle}
        Why Now: {why_now}
        Ultimate Goal: {sovereign_goal}
        Additional Context: {context}

        INTEGRAL COACHING APPROACH:
        1. Match your language and recommendations to their {likely_stage} developmental stage
        2. Address all AQAL quadrants: I (consciousness), IT (behavior), WE (relationships), ITS (systems)
        3. Honor their sovereignty path while supporting vertical development
        4. Provide both "growing up" (skills/habits) and "waking up" (consciousness) guidance
        5. Be direct, motivational, and sovereignty-focused - speak like a coach preparing them for battle

        Respond with powerful, stage-appropriate coaching that meets them where they are developmentally while pointing toward their growing edge. Don't mention developmental stages explicitly - just embody the appropriate level of complexity and values.
        """

        client.beta.threads.messages.create(
            thread_id=st.session_state.coaching_thread_id,
            role="user",
            content=user_prompt
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
            render_tracker_from_reply(reply)

# Step 2: Enhanced follow-up conversation with developmental awareness
if st.session_state.get("coaching_started"):
    st.subheader("🗣️ Continue the conversation with your Sovereignty Coach")
    
    # Show developmental stage in sidebar (for debugging/insight)
    if "developmental_stage" in st.session_state:
        st.sidebar.markdown(f"### 🧠 Developmental Profile")
        st.sidebar.markdown(f"**Stage:** {st.session_state.developmental_stage}")
        stage_descriptions = {
            "Orange": "Achievement-focused, metrics-driven",
            "Green": "Community-oriented, holistically-minded", 
            "Teal": "Systems-thinking, complexity-comfortable",
            "Turquoise": "Transpersonal, evolution-focused"
        }
        st.sidebar.markdown(f"*{stage_descriptions.get(st.session_state.developmental_stage, 'Integral approach')}*")

    for msg in st.session_state.coaching_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                render_tracker_from_reply(msg["content"])

    follow_up = st.chat_input("Continue the coaching conversation...")

    if follow_up:
        with st.chat_message("user"):
            st.markdown(follow_up)

        st.session_state.coaching_messages.append({"role": "user", "content": follow_up})

        # Enhanced follow-up prompt with stage awareness
        enhanced_follow_up = f"""
        Continue coaching this {st.session_state.get('developmental_stage', 'Orange')} stage user on their sovereignty path.
        
        User follow-up: {follow_up}
        
        Maintain stage-appropriate language and complexity. Stay focused on sovereignty principles and practical action.
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

        with st.spinner("🧠 Coach is integrating your developmental profile..."):
            while True:
                run = client.beta.threads.runs.retrieve(thread_id=st.session_state.coaching_thread_id, run_id=run.id)
                if run.status == "completed":
                    break
                time.sleep(1)

        messages = client.beta.threads.messages.list(thread_id=st.session_state.coaching_thread_id)
        reply = messages.data[0].content[0].text.value

        with st.chat_message("assistant"):
            st.markdown(reply)
            render_tracker_from_reply(reply)

        st.session_state.coaching_messages.append({"role": "assistant", "content": reply})