import streamlit as st
import os
from datetime import datetime

st.set_page_config(
    page_title="AI Meal Plan",
    page_icon="🍽️",
    layout="wide"
)

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
    
    # Dietary preferences
    diet_type = st.selectbox(
        "Select your dietary preference",
        ["Omnivore", "Vegetarian", "Vegan", "Paleo", "Keto", "Mediterranean", "Other"]
    )
    
    # Meal preferences
    meals_per_day = st.selectbox(
        "How many meals do you eat per day?",
        ["2 meals", "3 meals", "4 meals", "5+ meals"]
    )
    
    # Cooking time
    cooking_time = st.selectbox(
        "How much time can you spend cooking?",
        ["Quick & Easy (< 15 mins)", "Moderate (15-30 mins)", "Elaborate (30+ mins)"]
    )
    
    # Dietary restrictions
    restrictions = st.multiselect(
        "Any dietary restrictions?",
        ["Gluten-free", "Dairy-free", "Nut-free", "Shellfish-free", "None"]
    )
    
    # Goals
    goals = st.multiselect(
        "What are your goals?",
        ["Weight loss", "Muscle gain", "Energy boost", "Better digestion", "Reduce inflammation"]
    )
    
    # Additional preferences
    preferences = st.text_area(
        "Any additional preferences or notes",
        placeholder="Share any food preferences, allergies, or specific ingredients you'd like to include/avoid..."
    )
    
    submitted = st.form_submit_button("Generate Meal Plan")

if submitted:
    # TODO: Replace with actual AI agent call
    st.info("🤖 AI Chef is creating your meal plan...")
    
    # Placeholder response
    st.success("""
    Here's your personalized meal plan for the week:
    
    **Monday**
    - Breakfast: Protein smoothie with berries and spinach
    - Lunch: Quinoa bowl with roasted vegetables
    - Dinner: Grilled salmon with sweet potato
    
    **Tuesday**
    - Breakfast: Overnight oats with nuts and fruit
    - Lunch: Mediterranean salad with chickpeas
    - Dinner: Stir-fry with tofu and vegetables
    
    Would you like me to:
    1. Show the rest of the week's plan
    2. Provide recipes for any of these meals
    3. Adjust the plan based on your feedback
    """)
    
    # Add a feedback section
    st.subheader("How well does this meal plan match your needs?")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("👍 Perfect Match")
    with col2:
        st.button("😐 Needs Some Adjustments")
    with col3:
        st.button("👎 Not What I'm Looking For") 