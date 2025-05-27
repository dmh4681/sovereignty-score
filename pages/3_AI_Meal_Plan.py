import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv
import time

st.set_page_config(page_title="AI Meal Plan", page_icon="🍽️", layout="wide")

# Load API key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MEAL_ASSISTANT_ID = "asst_oKawT4ABxqNaXbUFsRq7vHIS"

client = OpenAI(api_key=OPENAI_API_KEY)

# Get user info from session state
username = st.session_state.get("username", None)
path = st.session_state.get("path", None)

if not username or not path:
    st.error("Please log in through the main page to access AI Meal Planning.")
    st.stop()

st.title("🍽️ AI Meal Plan")
st.sidebar.markdown(f"### Logged in as {username}")
st.sidebar.markdown(f"### Path: {path.replace('_',' ').title()}")

# Form for meal plan request
with st.form("meal_plan_form"):
    st.subheader("Let's create your personalized meal plan")
    diet_type = st.selectbox("Select your dietary preference", [
        "Omnivore", "Vegetarian", "Vegan", "Paleo", "Keto", "Mediterranean", "Other"])
    meals_per_day = st.selectbox("How many meals do you eat per day?", [
        "2 meals", "3 meals", "4 meals", "5+ meals"])
    cooking_time = st.selectbox("How much time can you spend cooking?", [
        "Quick & Easy (< 15 mins)", "Moderate (15-30 mins)", "Elaborate (30+ mins)"])
    restrictions = st.multiselect("Any dietary restrictions?", [
        "Gluten-free", "Dairy-free", "Nut-free", "Shellfish-free", "None"])
    goals = st.multiselect("What are your goals?", [
        "Weight loss", "Muscle gain", "Energy boost", "Better digestion", "Reduce inflammation"])
    preferences = st.text_area("Any additional preferences or notes", placeholder="Share any food preferences, allergies, or specific ingredients you'd like to include/avoid...")
    submitted = st.form_submit_button("Generate Meal Plan")

if submitted:
    st.info("🤖 AI Chef is creating your meal plan...")

    user_prompt = (
        f"Username: {username}\n"
        f"Sovereignty Path: {path.replace('_',' ')}\n"
        f"Diet Type: {diet_type}\n"
        f"Meals Per Day: {meals_per_day}\n"
        f"Cooking Time: {cooking_time}\n"
        f"Dietary Restrictions: {', '.join(restrictions)}\n"
        f"Goals: {', '.join(goals)}\n"
        f"Preferences: {preferences}"
    )

    thread = client.beta.threads.create()
    client.beta.threads.messages.create(thread_id=thread.id, role="user", content=user_prompt)
    run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=MEAL_ASSISTANT_ID)

    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run.status == "completed":
            break
        time.sleep(1)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    reply = messages.data[0].content[0].text.value
    st.success(reply)
