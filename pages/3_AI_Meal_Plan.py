#!/usr/bin/env python3
"""
Advanced AI Meal Planning Agent - Sovereignty-Aligned Nutrition
Generates personalized meal plans based on user's sovereignty path, behavioral data, and preferences
"""

import streamlit as st
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv
import time
import json
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO

# Setup paths for imports
project_root = os.path.dirname(os.path.dirname(__file__))
private_path = os.path.join(project_root, "Private")

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if private_path not in sys.path:
    sys.path.insert(0, private_path)

from db import get_db_connection
from sovereignty_achievements import SovereigntyAchievementEngine

# Page config
st.set_page_config(page_title="AI Meal Planning", page_icon="🍽️", layout="wide")

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("❌ OpenAI API key not found. Please check your .env file.")
    st.stop()

# Custom CSS for meal planning interface
st.markdown("""
<style>
    .meal-plan-card {
        background: linear-gradient(135deg, #1f2937, #374151);
        border: 2px solid #10b981;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
    }
    
    .nutrition-metric {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        margin: 5px 0;
    }
    
    .sovereignty-score {
        background: linear-gradient(45deg, #6366f1, #8b5cf6);
        color: white;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .meal-card {
        background: rgba(16, 185, 129, 0.05);
        border-left: 4px solid #10b981;
        padding: 15px;
        margin: 10px 0;
        border-radius: 0 8px 8px 0;
    }
</style>
""", unsafe_allow_html=True)

class AdvancedMealPlanningAgent:
    """
    Advanced meal planning agent that integrates sovereignty principles,
    user behavioral data, and personalized nutrition optimization
    """
    
    def __init__(self, openai_api_key):
        self.client = OpenAI(api_key=openai_api_key)
        self.assistant_id = self._create_meal_planning_assistant()
        
    def _create_meal_planning_assistant(self):
        """Create or retrieve the meal planning assistant"""
        
        assistant_instructions = """
You are the Sovereignty Meal Planning Agent, a master nutritionist who creates meal plans that build personal sovereignty through optimal nutrition aligned with individual paths and goals.

CORE PRINCIPLES:
- Food is medicine and fuel for sovereignty
- Home cooking = independence from industrial food systems
- Meal prep = time sovereignty and financial efficiency
- Nutritional optimization = cognitive and physical performance
- Sustainable eating = planetary and personal health

PATH-SPECIFIC APPROACHES:
- Financial Path: Cost-effective, bulk-prep focused, Bitcoin-earning efficiency
- Physical Optimization: High-protein, performance-focused, macro-optimized
- Spiritual Growth: Plant-forward, mindful eating, sustainable sourcing
- Mental Resilience: Brain-boosting nutrients, steady energy, anti-inflammatory
- Planetary Stewardship: Regenerative, local, minimal environmental impact
- Default/Balanced: Well-rounded approach across all sovereignty domains

EXPERT KNOWLEDGE INTEGRATION:
- Michael Pollan: "Eat food, not too much, mostly plants" + home cooking emphasis
- Andrew Huberman: Circadian nutrition, meal timing, cognitive performance foods
- Jeff Cavaliere: Protein optimization, meal prep efficiency, performance nutrition
- Mark Hyman: Anti-inflammatory eating, food as medicine, systems approach

REALISTIC COST ESTIMATION:
When providing cost estimates, use realistic 2025 grocery prices:
- Proteins: Chicken breast $4-6/lb, Ground beef $5-7/lb, Salmon $12-15/lb, Eggs $3-4/dozen
- Vegetables: Fresh produce $1-4/lb depending on type and season
- Grains: Rice/oats $1-2/lb, Quinoa $4-6/lb, Bread $2-4/loaf
- Pantry staples: Olive oil $8-12/bottle, Spices $2-5 each, Nuts $6-10/lb
- Weekly grocery budget realistic ranges: Budget-conscious $50-80, Moderate $80-120, Premium $120-180

Include quantity estimates and calculate realistic totals. Don't lowball costs - people need accurate budgeting info.

OUTPUT FORMAT:
Your response should be structured JSON that includes:

{
  "meal_plan": {
    "overview": "Brief summary of the approach and philosophy",
    "daily_structure": "Meal timing and structure explanation",
    "sovereignty_alignment": "How this plan builds sovereignty for this user"
  },
  "weekly_meals": {
    "breakfast": [{"name": "meal name", "prep_time": "X mins", "sovereignty_benefits": "why this meal builds sovereignty"}],
    "lunch": [...],
    "dinner": [...],
    "snacks": [...]
  },
  "shopping_list": {
    "proteins": ["item", "estimated cost"],
    "vegetables": ["item", "estimated cost"],
    "grains_starches": ["item", "estimated cost"],
    "fats_oils": ["item", "estimated cost"],
    "pantry_staples": ["item", "estimated cost"],
    "estimated_weekly_cost": "$X"
  },
  "meal_prep_strategy": {
    "prep_day_plan": "Step-by-step meal prep approach",
    "time_investment": "Total time needed",
    "efficiency_tips": ["tip1", "tip2", "tip3"]
  },
  "nutrition_analysis": {
    "daily_macros": {"protein": "Xg", "carbs": "Xg", "fat": "Xg", "calories": "X"},
    "key_nutrients": ["nutrient focus areas"],
    "sovereignty_score": "X/100 (explanation of score)"
  },
  "path_optimization": {
    "specific_benefits": "How this plan optimizes for their chosen sovereignty path",
    "habit_integration": "How to integrate with their current sovereignty habits",
    "progression_suggestions": "How to advance this plan over time"
  }
}

Always provide practical, actionable meal plans that someone can actually execute while building their sovereignty through nutrition.
"""
        
        try:
            assistant = self.client.beta.assistants.create(
                name="Sovereignty Meal Planning Agent",
                instructions=assistant_instructions,
                model="gpt-4o",
                tools=[]
            )
            return assistant.id
        except Exception as e:
            st.error(f"Error creating meal planning assistant: {e}")
            return None
    
    def generate_meal_plan(self, user_data, preferences):
        """Generate a personalized sovereignty meal plan"""
        
        # Create comprehensive prompt
        prompt = self._create_meal_plan_prompt(user_data, preferences)
        
        try:
            # Create thread and get response
            thread = self.client.beta.threads.create()
            
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=prompt
            )
            
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.assistant_id
            )
            
            # Wait for completion
            while True:
                run = self.client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
                if run.status == "completed":
                    break
                elif run.status in ["failed", "cancelled", "expired"]:
                    raise Exception(f"Assistant run failed: {run.status}")
                time.sleep(1)
            
            # Get response
            messages = self.client.beta.threads.messages.list(thread_id=thread.id)
            response = messages.data[0].content[0].text.value
            
            # Parse JSON response
            try:
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0].strip()
                else:
                    json_str = response
                
                meal_plan = json.loads(json_str)
                return meal_plan
                
            except json.JSONDecodeError:
                # If JSON parsing fails, return structured response
                return {
                    "meal_plan": {
                        "overview": "Custom meal plan generated",
                        "sovereignty_alignment": "Aligned with your sovereignty path"
                    },
                    "raw_response": response
                }
                
        except Exception as e:
            st.error(f"Error generating meal plan: {e}")
            return None
    
    def _create_meal_plan_prompt(self, user_data, preferences):
        """Create comprehensive prompt for meal plan generation"""
        
        # Extract user information
        username = user_data.get("username", "User")
        path = user_data.get("path", "default")
        achievements = user_data.get("achievements", {})
        
        # Build prompt
        prompt = f"""
SOVEREIGNTY MEAL PLAN REQUEST

User Profile:
- Username: {username}
- Sovereignty Path: {path.replace('_', ' ').title()}
- Current Level: {achievements.get('sovereignty_level', {}).get('name', 'Unknown')}

User Sovereignty Context:
- Total Days Tracked: {achievements.get('progress_metrics', {}).get('total_tracking_days', 0)}
- Meals Cooked: {achievements.get('progress_metrics', {}).get('total_meals_cooked', 0)}
- Current Streaks: {achievements.get('progress_metrics', {}).get('current_streaks', {})}

Dietary Preferences:
- Diet Type: {preferences.get('diet_type', 'Omnivore')}
- Meals Per Day: {preferences.get('meals_per_day', '3 meals')}
- Cooking Time Available: {preferences.get('cooking_time', 'Moderate')}
- Dietary Restrictions: {preferences.get('restrictions', [])}
- Health Goals: {preferences.get('goals', [])}
- Fasting Window: {preferences.get('fasting_window', 'No')}
- Budget Consideration: {preferences.get('budget_level', 'Moderate')}
- Meal Prep Style: {preferences.get('prep_style', 'Batch cook & store')}
- Calorie Needs: {preferences.get('calorie_tier', 'Moderate')}
- Additional Preferences: {preferences.get('preferences', 'None specified')}

Please create a comprehensive meal plan that:
1. Aligns with their sovereignty path principles
2. Supports their current sovereignty journey and achievements
3. Meets their dietary preferences and restrictions
4. Optimizes for their available time and budget
5. Includes practical meal prep strategies
6. Provides sovereignty-building benefits beyond just nutrition

Focus on meals that build independence, save money, boost performance, and align with their chosen sovereignty path.
"""
        
        return prompt

# Main Streamlit Interface
def main():
    # Get user info
    username = st.session_state.get("username", None)
    path = st.session_state.get("path", None)

    if not username or not path:
        st.error("🚨 Please log in through the main page to access AI Meal Planning.")
        st.stop()

    # Header
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: #10b981; margin: 0;">🍽️ AI Meal Planning</h1>
        <h3 style="color: #9ca3af; margin: 5px 0;">Sovereignty-Aligned Nutrition</h3>
        <p style="color: #6b7280; margin: 0;">Welcome back, {username} | Path: {path.replace('_', ' ').title()}</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize meal planning agent
    @st.cache_resource
    def get_meal_agent():
        return AdvancedMealPlanningAgent(OPENAI_API_KEY)

    meal_agent = get_meal_agent()
    
    if not meal_agent.assistant_id:
        st.error("❌ Could not initialize meal planning agent")
        st.stop()

    # Load user achievements for context
    @st.cache_data(ttl=300)
    def get_user_context(username):
        """Get user context including achievements"""
        try:
            engine = SovereigntyAchievementEngine()
            achievements = engine.calculate_user_achievements(username)
            return {
                "username": username,
                "path": path,
                "achievements": achievements
            }
        except Exception as e:
            return {"username": username, "path": path, "achievements": {}}

    user_data = get_user_context(username)

    # Meal Plan Generation Form
    st.markdown("## 📋 Meal Plan Preferences")
    
    with st.form("advanced_meal_plan_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🥘 Dietary Preferences")
            diet_type = st.selectbox("Diet Type", [
                "Omnivore", "Vegetarian", "Vegan", "Paleo", "Keto", 
                "Mediterranean", "Carnivore", "Plant-Based", "Other"
            ])
            
            meals_per_day = st.selectbox("Meals Per Day", [
                "2 meals (OMAD/IF)", "3 meals (standard)", "4 meals (frequent)", 
                "5+ meals (athlete/bulk)"
            ])
            
            cooking_time = st.selectbox("Available Cooking Time", [
                "Minimal (< 15 mins)", "Moderate (15-45 mins)", 
                "Extensive (45+ mins)", "Weekend warrior (batch prep)"
            ])
            
            restrictions = st.multiselect("Dietary Restrictions", [
                "Gluten-free", "Dairy-free", "Nut allergies", "Shellfish allergies",
                "Egg-free", "Soy-free", "Low-sodium", "Low-FODMAP", "None"
            ])
        
        with col2:
            st.markdown("### 🎯 Goals & Optimization")
            goals = st.multiselect("Primary Goals", [
                "Fat loss", "Muscle gain", "Energy optimization", "Cognitive performance",
                "Digestive health", "Anti-inflammatory", "Longevity", "Athletic performance",
                "Budget optimization", "Time efficiency"
            ])
            
            fasting_window = st.selectbox("Eating Window", [
                "No restrictions", "16:8 Intermittent Fasting", "14:10 Time-restricted",
                "20:4 (One meal + snack)", "OMAD (One meal a day)", "Custom schedule"
            ])
            
            budget_level = st.selectbox("Budget Priority", [
                "High (optimize for cost)", "Moderate (balance cost/quality)", 
                "Low (premium ingredients okay)"
            ])
            
            prep_style = st.selectbox("Meal Prep Approach", [
                "Daily fresh cooking", "Weekly batch prep", "Hybrid (some prep)",
                "Minimal prep (simple assembly)"
            ])
        
        st.markdown("### 📊 Caloric & Performance Needs")
        calorie_tier = st.selectbox("Caloric Needs", [
            "Low (1,200-1,600 kcal) - Fat loss focus",
            "Moderate (1,600-2,200 kcal) - Maintenance", 
            "High (2,200-2,800 kcal) - Active lifestyle",
            "Very High (2,800-3,500+ kcal) - Athlete/bulking"
        ])
        
        preferences = st.text_area(
            "Additional Preferences & Context",
            placeholder="Share any specific foods you love/hate, cultural preferences, health conditions, sovereignty goals, or other relevant context...",
            height=100
        )
        
        submitted = st.form_submit_button("🚀 Generate Sovereignty Meal Plan", type="primary")

    if submitted:
        # Collect preferences
        user_preferences = {
            "diet_type": diet_type,
            "meals_per_day": meals_per_day,
            "cooking_time": cooking_time,
            "restrictions": restrictions,
            "goals": goals,
            "fasting_window": fasting_window,
            "budget_level": budget_level,
            "prep_style": prep_style,
            "calorie_tier": calorie_tier,
            "preferences": preferences
        }
        
        # Store preferences in session state to persist after downloads
        st.session_state.meal_preferences = user_preferences
        st.session_state.generate_meal_plan = True

    # Generate meal plan (either from form submission or session state)
    if st.session_state.get("generate_meal_plan", False):
        user_preferences = st.session_state.get("meal_preferences", {})
        
        # Only generate if we don't already have a plan for these preferences
        if "current_meal_plan" not in st.session_state or st.session_state.get("meal_preferences_hash") != hash(str(user_preferences)):
            with st.spinner("🧠 AI Chef is crafting your sovereignty-aligned meal plan..."):
                meal_plan = meal_agent.generate_meal_plan(user_data, user_preferences)
                
                if meal_plan:
                    st.session_state.current_meal_plan = meal_plan
                    st.session_state.meal_preferences_hash = hash(str(user_preferences))
                else:
                    st.error("❌ Failed to generate meal plan. Please try again.")
                    st.session_state.generate_meal_plan = False
                    st.stop()
        
        # Display the meal plan from session state
        meal_plan = st.session_state.get("current_meal_plan")
        if meal_plan:
            display_meal_plan(meal_plan, user_preferences)

def display_meal_plan(meal_plan, preferences):
    """Display the generated meal plan in an attractive format"""
    
    st.markdown("---")
    st.markdown("## 🍽️ Your Sovereignty Meal Plan")
    
    # Overview section
    if "meal_plan" in meal_plan:
        overview = meal_plan["meal_plan"]
        
        st.markdown("### 📖 Plan Overview")
        st.markdown(f"**Philosophy:** {overview.get('overview', 'Custom sovereignty nutrition approach')}")
        st.markdown(f"**Structure:** {overview.get('daily_structure', 'Optimized for your preferences')}")
        
        # Sovereignty alignment score
        if "nutrition_analysis" in meal_plan:
            nutrition = meal_plan["nutrition_analysis"]
            sovereignty_score = nutrition.get("sovereignty_score", "85/100 - Strong sovereignty alignment")
            
            st.markdown(f"""
            <div class="sovereignty-score">
                🛡️ Sovereignty Score: {sovereignty_score}
            </div>
            """, unsafe_allow_html=True)
    
    # Nutrition metrics
    if "nutrition_analysis" in meal_plan:
        st.markdown("### 📊 Nutrition Analysis")
        nutrition = meal_plan["nutrition_analysis"]
        
        col1, col2, col3, col4 = st.columns(4)
        macros = nutrition.get("daily_macros", {})
        
        with col1:
            st.markdown(f"""
            <div class="nutrition-metric">
                <h3>{macros.get('calories', 'N/A')}</h3>
                <p>Calories</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="nutrition-metric">
                <h3>{macros.get('protein', 'N/A')}</h3>
                <p>Protein</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="nutrition-metric">
                <h3>{macros.get('carbs', 'N/A')}</h3>
                <p>Carbs</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="nutrition-metric">
                <h3>{macros.get('fat', 'N/A')}</h3>
                <p>Fat</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Weekly meals
    if "weekly_meals" in meal_plan:
        st.markdown("### 🗓️ Weekly Meal Structure")
        
        meals = meal_plan["weekly_meals"]
        meal_types = ["breakfast", "lunch", "dinner", "snacks"]
        
        for meal_type in meal_types:
            if meal_type in meals and meals[meal_type]:
                st.markdown(f"#### {meal_type.title()}")
                
                for i, meal in enumerate(meals[meal_type][:3]):  # Show first 3 options
                    st.markdown(f"""
                    <div class="meal-card">
                        <h4>{meal.get('name', f'{meal_type.title()} Option {i+1}')}</h4>
                        <p><strong>Prep Time:</strong> {meal.get('prep_time', 'Quick')}</p>
                        <p><strong>Sovereignty Benefits:</strong> {meal.get('sovereignty_benefits', 'Builds nutritional independence')}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Shopping list and meal prep
    col1, col2 = st.columns(2)
    
    with col1:
        if "shopping_list" in meal_plan:
            st.markdown("### 🛒 Shopping List")
            shopping = meal_plan["shopping_list"]
            
            categories = ["proteins", "vegetables", "grains_starches", "fats_oils", "pantry_staples"]
            for category in categories:
                if category in shopping:
                    st.markdown(f"**{category.replace('_', ' ').title()}:**")
                    items = shopping[category]
                    for item in items[:5]:  # Show first 5 items
                        st.markdown(f"• {item}")
            
            estimated_cost = shopping.get("estimated_weekly_cost", "Estimate not available")
            st.markdown(f"**💰 Estimated Weekly Cost:** {estimated_cost}")
    
    with col2:
        if "meal_prep_strategy" in meal_plan:
            st.markdown("### 🥘 Meal Prep Strategy")
            prep = meal_plan["meal_prep_strategy"]
            
            st.markdown(f"**⏱️ Time Investment:** {prep.get('time_investment', 'Efficient prep strategy')}")
            st.markdown(f"**📋 Prep Plan:** {prep.get('prep_day_plan', 'Organized preparation approach')}")
            
            tips = prep.get("efficiency_tips", [])
            if tips:
                st.markdown("**💡 Efficiency Tips:**")
                for tip in tips[:3]:
                    st.markdown(f"• {tip}")
    
    # Path optimization
    if "path_optimization" in meal_plan:
        st.markdown("### 🛡️ Sovereignty Path Optimization")
        optimization = meal_plan["path_optimization"]
        
        st.markdown(f"**🎯 Path Benefits:** {optimization.get('specific_benefits', 'Optimized for your sovereignty journey')}")
        st.markdown(f"**🔄 Habit Integration:** {optimization.get('habit_integration', 'Seamlessly integrates with your current habits')}")
        st.markdown(f"**📈 Progression:** {optimization.get('progression_suggestions', 'Strategies for advancing your nutrition sovereignty')}")
    
    # Download options
    st.markdown("### 📥 Export Options")
    
    # Create download data first
    shopping_data = meal_plan.get("shopping_list", {})
    meal_data = []
    if "weekly_meals" in meal_plan:
        for meal_type, meals in meal_plan["weekly_meals"].items():
            for meal in meals:
                meal_data.append({
                    "Type": meal_type.title(),
                    "Name": meal.get("name", ""),
                    "Prep Time": meal.get("prep_time", ""),
                    "Benefits": meal.get("sovereignty_benefits", "")
                })
    
    # Shopping list download
    def create_shopping_download():
        df_shopping = pd.DataFrame([(k, str(v)) for k, v in shopping_data.items()], 
                                 columns=["Category", "Items"])
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df_shopping.to_excel(writer, index=False, sheet_name="Shopping List")
        buffer.seek(0)
        return buffer.getvalue()
    
    # Meal plan download
    def create_meal_download():
        df_meals = pd.DataFrame(meal_data)
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df_meals.to_excel(writer, index=False, sheet_name="Meal Plan")
        buffer.seek(0)
        return buffer.getvalue()
    
    # Full plan download
    def create_full_download():
        plan_summary = {
            "Plan Overview": meal_plan.get("meal_plan", {}).get("overview", ""),
            "Sovereignty Alignment": meal_plan.get("meal_plan", {}).get("sovereignty_alignment", ""),
            "Daily Calories": meal_plan.get("nutrition_analysis", {}).get("daily_macros", {}).get("calories", ""),
            "Estimated Cost": meal_plan.get("shopping_list", {}).get("estimated_weekly_cost", ""),
            "Prep Time": meal_plan.get("meal_prep_strategy", {}).get("time_investment", "")
        }
        
        df_summary = pd.DataFrame(list(plan_summary.items()), columns=["Aspect", "Details"])
        df_meals = pd.DataFrame(meal_data)
        
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df_summary.to_excel(writer, index=False, sheet_name="Plan Summary")
            if not df_meals.empty:
                df_meals.to_excel(writer, index=False, sheet_name="Meals")
            
            # Add shopping list sheet
            if shopping_data:
                df_shopping = pd.DataFrame([(k, str(v)) for k, v in shopping_data.items()], 
                                         columns=["Category", "Items"])
                df_shopping.to_excel(writer, index=False, sheet_name="Shopping List")
        
        buffer.seek(0)
        return buffer.getvalue()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            label="📋 Download Shopping List",
            data=create_shopping_download(),
            file_name=f"sovereignty_shopping_list_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        st.download_button(
            label="🍽️ Download Meal Plan", 
            data=create_meal_download(),
            file_name=f"sovereignty_meal_plan_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col3:
        st.download_button(
            label="📊 Download Full Plan",
            data=create_full_download(),
            file_name=f"complete_sovereignty_plan_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

if __name__ == "__main__":
    main()