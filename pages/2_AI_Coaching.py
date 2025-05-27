import streamlit as st
import os
from datetime import datetime

st.set_page_config(
    page_title="AI Coaching",
    page_icon="🧠",
    layout="wide"
)

# Get user info from session state
username = st.session_state.get("username", None)
path = st.session_state.get("path", None)

if not username or not path:
    st.error("Please log in through the main page to access AI Coaching.")
    st.stop()

st.title("🧠 AI Coaching")
st.sidebar.markdown(f"### Logged in as {username}")
st.sidebar.markdown(f"### Path: {path.replace('_',' ').title()}")

# Form for coaching request
with st.form("coaching_form"):
    st.subheader("What would you like coaching on?")
    
    # Area of focus
    focus_area = st.selectbox(
        "Select your focus area",
        ["Physical Health", "Mental Wellbeing", "Financial Growth", "Environmental Impact", "Spiritual Development"]
    )
    
    # Current challenge
    challenge = st.text_area(
        "Describe your current challenge or goal",
        placeholder="I'm struggling with... or I want to achieve..."
    )
    
    # Time commitment
    time_commitment = st.selectbox(
        "How much time can you commit daily?",
        ["5-15 minutes", "15-30 minutes", "30-60 minutes", "1-2 hours", "2+ hours"]
    )
    
    # Additional context
    context = st.text_area(
        "Any additional context (optional)",
        placeholder="Share any relevant details about your situation, preferences, or constraints..."
    )
    
    submitted = st.form_submit_button("Get AI Coaching")

if submitted:
    # TODO: Replace with actual AI agent call
    st.info("🤖 AI Coach is thinking...")
    
    # Placeholder response
    st.success("""
    Based on your inputs, here's your personalized coaching plan:
    
    1. **Daily Practice (15 minutes)**
       - Morning meditation focusing on your specific challenge
       - Evening reflection on progress
    
    2. **Weekly Goals**
       - Set 3 specific, measurable goals
       - Track progress in your Sovereignty Score
    
    3. **Recommended Resources**
       - Book: "Atomic Habits" by James Clear
       - App: Headspace for guided meditation
    
    Would you like me to elaborate on any of these points?
    """)
    
    # Add a feedback section
    st.subheader("How helpful was this coaching?")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("👍 Very Helpful")
    with col2:
        st.button("😐 Somewhat Helpful")
    with col3:
        st.button("👎 Not Helpful") 