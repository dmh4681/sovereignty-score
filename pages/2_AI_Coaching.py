import streamlit as st
import os
import time
from openai import OpenAI
from dotenv import load_dotenv

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

st.title("🧠 AI Coaching")
st.sidebar.markdown(f"### Logged in as {username}")
st.sidebar.markdown(f"### Path: {path.replace('_',' ').title()}")

if st.sidebar.button("🔄 Reset Session"):
    st.session_state.pop("coaching_thread_id", None)
    st.session_state.pop("coaching_messages", None)
    st.session_state.pop("coaching_started", None)
    st.rerun()


# 🧠 Thread & message history
if "coaching_thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.coaching_thread_id = thread.id
    st.session_state.coaching_messages = []

# Step 1: Initial structured coaching form
if "coaching_started" not in st.session_state:

    with st.form("coaching_form"):
        st.subheader("What would you like coaching on?")
        focus_area = st.selectbox("Select your focus area", [
            "Physical Health", "Mental Wellbeing", "Financial Growth", "Environmental Impact", "Spiritual Development"])
        challenge = st.text_area("Describe your current challenge or goal", placeholder="I'm struggling with... or I want to achieve...")
        time_commitment = st.selectbox("How much time can you commit daily?", [
            "5-15 minutes", "15-30 minutes", "30-60 minutes", "1-2 hours", "2+ hours"])
        context = st.text_area("Any additional context (optional)", placeholder="Share any relevant details about your situation, preferences, or constraints...")
        obstacle = st.selectbox("What tends to derail your consistency?", [
            "Lack of time", "Low motivation", "Mental distraction", "Overwhelm", "Lack of clarity", "Other"])
        why_now = st.text_area("Why do you want to improve this now?", placeholder="What’s driving this shift at this point in your life?")
        sovereign_goal = st.text_area("If this challenge was resolved, what would that unlock for you?", placeholder="Describe your desired future state...")
        submitted = st.form_submit_button("Get AI Coaching")

    if submitted:
        st.info("🤖 AI Coach is thinking...")

        user_prompt = (
            f"You are a Sovereign Coach. Speak to me as if I’m your top performer preparing for battle.\n"
            f"Username: {username}\n"
            f"Sovereignty Path: {path.replace('_',' ')}\n"
            f"Focus Area: {focus_area}\n"
            f"Challenge: {challenge}\n"
            f"Time Commitment: {time_commitment}\n"
            f"Context: {context}\n"
            f"Obstacle: {obstacle}\n"
            f"Why Now: {why_now}\n"
            f"Ultimate Goal: {sovereign_goal}"
        )

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

# Step 2: Follow-up conversation loop (chat-style)
if st.session_state.get("coaching_started"):
    st.subheader("Continue the conversation with your Coach")

    # Display full history
    for msg in st.session_state.coaching_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input box for follow-up
    follow_up = st.chat_input("Ask a follow-up question...")

    if follow_up:
        with st.chat_message("user"):
            st.markdown(follow_up)

        st.session_state.coaching_messages.append({"role": "user", "content": follow_up})

        client.beta.threads.messages.create(
            thread_id=st.session_state.coaching_thread_id,
            role="user",
            content=follow_up
        )

        run = client.beta.threads.runs.create(
            thread_id=st.session_state.coaching_thread_id,
            assistant_id=COACHING_ASSISTANT_ID
        )

        with st.spinner("🧠 Coach is reflecting..."):
            while True:
                run = client.beta.threads.runs.retrieve(thread_id=st.session_state.coaching_thread_id, run_id=run.id)
                if run.status == "completed":
                    break
                time.sleep(1)

        messages = client.beta.threads.messages.list(thread_id=st.session_state.coaching_thread_id)
        reply = messages.data[0].content[0].text.value

        with st.chat_message("assistant"):
            st.markdown(reply)

        st.session_state.coaching_messages.append({"role": "assistant", "content": reply})
