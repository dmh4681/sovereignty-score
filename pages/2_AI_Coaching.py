import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv
import time

st.set_page_config(page_title="AI Coaching", page_icon="🧠", layout="wide")

# Load API key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COACHING_ASSISTANT_ID = "asst_I7akt1W4Je7c5U3cN1guiefc"

client = OpenAI(api_key=OPENAI_API_KEY)

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
    focus_area = st.selectbox("Select your focus area", [
        "Physical Health", "Mental Wellbeing", "Financial Growth", "Environmental Impact", "Spiritual Development"])
    challenge = st.text_area("Describe your current challenge or goal", placeholder="I'm struggling with... or I want to achieve...")
    time_commitment = st.selectbox("How much time can you commit daily?", [
        "5-15 minutes", "15-30 minutes", "30-60 minutes", "1-2 hours", "2+ hours"])
    context = st.text_area("Any additional context (optional)", placeholder="Share any relevant details about your situation, preferences, or constraints...")
    submitted = st.form_submit_button("Get AI Coaching")

if submitted:
    st.info("🤖 AI Coach is thinking...")

    user_prompt = (
        f"Username: {username}\n"
        f"Sovereignty Path: {path.replace('_',' ')}\n"
        f"Focus Area: {focus_area}\n"
        f"Challenge: {challenge}\n"
        f"Time Commitment: {time_commitment}\n"
        f"Context: {context}"
    )

    thread = client.beta.threads.create()
    client.beta.threads.messages.create(thread_id=thread.id, role="user", content=user_prompt)
    run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=COACHING_ASSISTANT_ID)

    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run.status == "completed":
            break
        time.sleep(1)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    reply = messages.data[0].content[0].text.value
    st.success(reply)
