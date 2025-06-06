#!/usr/bin/env python3
"""
Enhanced AI Meal Planning Agent - Sovereignty-Aligned Nutrition with Sidebar Profile
Now includes comprehensive sovereignty profile sidebar matching the AI Coaching page
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

# Enhanced CSS matching the coaching page style
st.markdown("""
<style>
    .meal-plan-hero {
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
    
    .nutrition-insight {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.1));
        border-left: 4px solid #10b981;
        padding: 16px;
        margin: 12px 0;
        border-radius: 0 8px 8px 0;
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
    
    .consciousness-indicator {
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 6px;
        padding: 8px;
        margin: 5px 0;
        font-size: 0.9em;
        text-align: center;
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
    
    .meal-plan-card {
        background: linear-gradient(135deg, #1f2937, #374151);
        border: 2px solid #10b981;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
    }
</style>
""", unsafe_allow_html=True)

class AdvancedMealPlanningAgent:
    """
    Advanced meal planning agent that integrates sovereignty principles,
    user behavioral data, and developmental consciousness intelligence
    """
    
    def __init__(self, openai_api_key):
        self.client = OpenAI(api_key=openai_api_key)
        self.assistant_id = self._create_meal_planning_assistant()
        
    def _create_meal_planning_assistant(self):
        """Create or retrieve the meal planning assistant with developmental awareness"""
        
        assistant_instructions = """
You are the Sovereignty Meal Planning Agent, a master nutritionist who creates meal plans that build personal sovereignty through optimal nutrition aligned with individual consciousness levels and sovereignty paths.

CORE PRINCIPLES:
- Food is medicine and fuel for sovereignty
- Home cooking = independence from industrial food systems
- Meal prep = time sovereignty and financial efficiency
- Nutritional optimization = cognitive and physical performance
- Sustainable eating = planetary and personal health

CONSCIOUSNESS-ADAPTED APPROACHES:
- Orange Level: Emphasize metrics, optimization, performance data, scientific backing, macro tracking, measurable results
- Green Level: Focus on holistic health, environmental connection, mindful eating, seasonal ingredients, intuitive approaches
- Teal Level: Integrate systems thinking, regenerative agriculture, complex interconnections, dynamic adaptation strategies
- Turquoise Level: Include transpersonal elements, food as spiritual practice, consciousness evolution through nutrition

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

DEVELOPMENTAL LANGUAGE ADAPTATION:
Match your language complexity, philosophical depth, and recommendation style to the user's consciousness level:
- Orange: Direct, data-driven, optimization-focused, practical efficiency
- Green: Holistic, mindful, environmentally conscious, intuitive wisdom
- Teal: Systems-oriented, complexity-comfortable, dynamically adaptive, interconnected thinking
- Turquoise: Transpersonal, spiritually-integrated, evolutionary perspective, unified approach

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
    "overview": "Brief summary matching their consciousness level",
    "daily_structure": "Meal timing and structure explanation",
    "sovereignty_alignment": "How this plan builds sovereignty for this user",
    "consciousness_approach": "How the plan matches their developmental level"
  },
  "weekly_meals": {
    "breakfast": [{"name": "meal name", "prep_time": "X mins", "sovereignty_benefits": "consciousness-appropriate benefits"}],
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
    "prep_day_plan": "Consciousness-appropriate prep approach",
    "time_investment": "Total time needed",
    "efficiency_tips": ["consciousness-level appropriate tips"]
  },
  "nutrition_analysis": {
    "daily_macros": {"protein": "Xg", "carbs": "Xg", "fat": "Xg", "calories": "X"},
    "key_nutrients": ["developmental-level appropriate focus areas"],
    "sovereignty_score": "X/100 (consciousness-appropriate explanation)"
  },
  "path_optimization": {
    "specific_benefits": "How this plan optimizes for their chosen sovereignty path",
    "habit_integration": "How to integrate with their current sovereignty habits",
    "progression_suggestions": "Consciousness-appropriate advancement strategies"
  }
}

Always provide practical, actionable meal plans that match the user's developmental sophistication while building sovereignty through nutrition.
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
        """Generate a personalized sovereignty meal plan with developmental intelligence"""
        
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
        """Create comprehensive prompt for meal plan generation with developmental intelligence"""
        
        # Extract user information
        username = user_data.get("username", "User")
        path = user_data.get("path", "default")
        achievements = user_data.get("achievements", {})
        
        # Determine developmental approach based on food philosophy
        food_philosophy_mapping = {
            "Precise nutrition and measurable results": "Orange",
            "Connection to nature and seasonal eating": "Green", 
            "Understanding food systems and sustainability": "Teal",
            "Food as medicine and spiritual nourishment": "Turquoise"
        }
        
        decision_mapping = {
            "Based on data, macros, and proven science": "Orange",
            "Intuitive eating with mindful awareness": "Green",
            "Systems thinking about long-term impacts": "Teal",
            "Holistic integration of body, mind, and spirit": "Turquoise"
        }
        
        # Determine consciousness level for food approach
        food_consciousness = food_philosophy_mapping.get(preferences.get('food_relationship', ''), 'Orange')
        decision_consciousness = decision_mapping.get(preferences.get('decision_style', ''), 'Orange')
        
        # Use the higher complexity level for recommendations
        consciousness_levels = ['Orange', 'Green', 'Teal', 'Turquoise']
        primary_level = consciousness_levels[max(
            consciousness_levels.index(food_consciousness),
            consciousness_levels.index(decision_consciousness)
        )]
        
        # Build prompt with developmental awareness
        prompt = f"""
SOVEREIGNTY MEAL PLAN REQUEST

User Profile:
- Username: {username}
- Sovereignty Path: {path.replace('_', ' ').title()}
- Current Level: {achievements.get('sovereignty_level', {}).get('name', 'Unknown')}
- Food Consciousness Level: {primary_level}

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
- Food Philosophy: {preferences.get('food_relationship', 'Not specified')}
- Decision Style: {preferences.get('decision_style', 'Not specified')}
- Additional Preferences: {preferences.get('preferences', 'None specified')}

DEVELOPMENTAL APPROACH GUIDANCE:
Based on their {primary_level} consciousness level, tailor your response:

- Orange Level: Focus on optimization, measurable results, performance metrics, scientific backing, macro tracking, efficiency
- Green Level: Emphasize holistic health, environmental impact, mindful eating, seasonal ingredients, intuitive approaches
- Teal Level: Integrate systems thinking, regenerative agriculture, complex interconnections, dynamic adaptation
- Turquoise Level: Include transpersonal elements, food as spiritual practice, consciousness evolution through nutrition

Please create a comprehensive meal plan that:
1. Matches their {primary_level} consciousness level in language and approach
2. Aligns with their sovereignty path principles
3. Supports their current sovereignty journey and achievements
4. Meets their dietary preferences and restrictions
5. Optimizes for their available time and budget
6. Includes practical meal prep strategies
7. Provides consciousness-appropriate sovereignty-building benefits

Adjust the complexity, language, and philosophical depth to match their developmental level while maintaining practical utility.
"""
        
        return prompt

# Replace the main interface section in your 3_AI_Meal_Plan.py 
# (after the class definitions, around line 200-400)

def main():
    # Get user info
    username = st.session_state.get("username", None)
    path = st.session_state.get("path", None)

    if not username or not path:
        st.error("🚨 Please log in through the main page to access AI Meal Planning.")
        st.stop()

    # Load comprehensive user data for sidebar
    @st.cache_data(ttl=300)
    def load_comprehensive_user_data(username):
        """Load all user data for enhanced meal planning sidebar"""
        try:
            engine = SovereigntyAchievementEngine()
            achievements_data = engine.calculate_user_achievements(username)
            
            with get_db_connection() as conn:
                recent_data = conn.execute("""
                    SELECT timestamp, score, home_cooked_meals, junk_food, exercise_minutes,
                           strength_training, no_spending, invested_bitcoin, btc_usd, btc_sats,
                           meditation, gratitude, read_or_learned, environmental_action
                    FROM sovereignty 
                    WHERE username = ? AND timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT 30
                """, [username, datetime.now() - timedelta(days=30)]).fetchall()
                
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
    with st.spinner("🔍 Loading your nutrition profile..."):
        user_data = load_comprehensive_user_data(username)

    if not user_data or "error" in user_data.get("achievements", {}):
        st.error("❌ Unable to load your sovereignty data. Please ensure you have tracking history.")
        st.stop()

    # Extract key insights
    achievements = user_data["achievements"]
    recent_tracking = user_data["recent_tracking"]
    sovereignty_level = achievements.get("sovereignty_level", {})
    earned_achievements = achievements.get("achievements_earned", [])
    progress_metrics = achievements.get("progress_metrics", {})
    next_achievements = achievements.get("next_achievements", [])
    current_streaks = progress_metrics.get("current_streaks", {})
    active_streaks = {k: v for k, v in current_streaks.items() if v > 0}

    # CONDENSED HEADER - Combined the two sections
    st.markdown(f"""
    <div class="meal-plan-hero">
        <h1>🍽️ Sovereignty Meal Planning</h1>
        <p style="margin: 8px 0; opacity: 0.9;">Nutrition as the foundation of freedom</p>
        <p style="margin: 0; font-size: 14px; opacity: 0.7;">Path: {path.replace('_', ' ').title()} • User: {username}</p>
    </div>
    """, unsafe_allow_html=True)

    # Enhanced Sidebar
    if st.sidebar.button("🔄 Reset Meal Plan"):
        st.session_state.pop("current_meal_plan", None)
        st.session_state.pop("meal_preferences", None)
        st.session_state.pop("generate_meal_plan", None)
        st.session_state.pop("meal_preferences_hash", None)
        st.session_state.pop("consciousness_level", None)
        st.rerun()

    st.sidebar.markdown("### 🛡️ Your Sovereignty Profile")
    st.sidebar.markdown(f"**Level:** {sovereignty_level.get('name', 'Unknown')}")
    st.sidebar.markdown(f"**Avg Score:** {sovereignty_level.get('avg_score', 0):.1f}")
    st.sidebar.markdown(f"**Total Days:** {sovereignty_level.get('total_days', 0)}")
    st.sidebar.markdown(f"**Achievements:** {len(earned_achievements)}")

    # Cooking profile in sidebar
    total_meals = progress_metrics.get("total_meals_cooked", 0)
    if total_meals > 0:
        st.sidebar.markdown("### 🍳 Cooking Profile")
        st.sidebar.markdown(f"**Total Meals Cooked:** {total_meals}")
        
        if recent_tracking:
            recent_meals = sum(row[2] for row in recent_tracking if row[2])
            cooking_days = len([row for row in recent_tracking if row[2] and row[2] > 0])
            if cooking_days > 0:
                avg_meals_per_day = recent_meals / len(recent_tracking) if recent_tracking else 0
                st.sidebar.markdown(f"**Recent Cooking Days:** {cooking_days}/30")
                st.sidebar.markdown(f"**Avg Meals/Day:** {avg_meals_per_day:.1f}")

    # Active streaks in sidebar
    if active_streaks:
        st.sidebar.markdown("### 🔥 Active Streaks")
        for activity, days in list(active_streaks.items())[:3]:
            emoji = {"meditation": "🧘‍♂️", "strength_training": "💪", "invested_bitcoin": "₿", 
                    "gratitude": "🙏", "environmental_action": "🌍", "cooking": "🍳"}.get(activity, "⚡")
            st.sidebar.markdown(f"{emoji} **{days}** {activity.replace('_', ' ').title()}")

    # Recent performance in sidebar
    if recent_tracking:
        recent_scores = [row[1] for row in recent_tracking if row[1] is not None]
        if recent_scores:
            recent_avg = sum(recent_scores) / len(recent_scores)
            st.sidebar.markdown(f"### 📈 Recent Performance")
            st.sidebar.markdown(f"**Last 7 days avg:** {recent_avg:.1f}")
            
            if len(recent_scores) >= 7:
                early_week = sum(recent_scores[:3]) / 3
                late_week = sum(recent_scores[-3:]) / 3
                trend = "📈 Improving" if late_week > early_week else "📉 Declining" if late_week < early_week else "➡️ Stable"
                st.sidebar.markdown(f"**Trend:** {trend}")

    # Path-specific tip in sidebar
    st.sidebar.markdown("### 🎯 Path Focus")
    path_nutrition_tips = {
        "financial_path": "Focus on cost-effective, bulk-prep meals",
        "physical_optimization": "Prioritize high-protein, performance nutrition",
        "spiritual_growth": "Emphasize plant-forward, mindful eating",
        "mental_resilience": "Choose brain-boosting, anti-inflammatory foods",
        "planetary_stewardship": "Select regenerative, locally-sourced ingredients",
        "default": "Balanced nutrition across all sovereignty domains"
    }
    
    nutrition_tip = path_nutrition_tips.get(path, "Balanced sovereignty nutrition")
    st.sidebar.markdown(f"*{nutrition_tip}*")

    # Initialize meal planning agent
    @st.cache_resource
    def get_meal_agent():
        return AdvancedMealPlanningAgent(OPENAI_API_KEY)

    meal_agent = get_meal_agent()
    
    if not meal_agent.assistant_id:
        st.error("❌ Could not initialize meal planning agent")
        st.stop()

    # Prepare user data for meal planning
    user_meal_data = {
        "username": username,
        "path": path,
        "achievements": achievements
    }

    # QUICK ACTION BUTTONS (The Magic!)
    st.markdown("## 🚀 Quick Meal Planning")
    
    quick_col1, quick_col2, quick_col3 = st.columns(3)
    
    with quick_col1:
        if st.button("🍽️ Quick meal plan for my path", key="quick_path_plan", use_container_width=True):
            # Generate path-optimized preferences automatically
            path_defaults = {
                "financial_path": {
                    "diet_type": "Omnivore",
                    "meals_per_day": "3 meals (standard)",
                    "cooking_time": "Weekend warrior (batch prep)",
                    "restrictions": ["None"],
                    "goals": ["Budget optimization", "Time efficiency"],
                    "fasting_window": "16:8 Intermittent Fasting",
                    "budget_level": "High (optimize for cost)",
                    "prep_style": "Weekly batch prep",
                    "calorie_tier": "Moderate (1,600-2,200 kcal) - Maintenance",
                    "preferences": "Focus on cost-effective, bulk ingredients for maximum Bitcoin stacking efficiency",
                    "food_relationship": "Precise nutrition and measurable results",
                    "decision_style": "Based on data, macros, and proven science"
                },
                "physical_optimization": {
                    "diet_type": "Omnivore",
                    "meals_per_day": "4 meals (frequent)",
                    "cooking_time": "Moderate (15-45 mins)",
                    "restrictions": ["None"],
                    "goals": ["Muscle gain", "Athletic performance", "Energy optimization"],
                    "fasting_window": "No restrictions",
                    "budget_level": "Moderate (balance cost/quality)",
                    "prep_style": "Weekly batch prep",
                    "calorie_tier": "High (2,200-2,800 kcal) - Active lifestyle",
                    "preferences": "High-protein focus for strength and performance optimization",
                    "food_relationship": "Precise nutrition and measurable results",
                    "decision_style": "Based on data, macros, and proven science"
                },
                "spiritual_growth": {
                    "diet_type": "Plant-Based",
                    "meals_per_day": "3 meals (standard)",
                    "cooking_time": "Moderate (15-45 mins)",
                    "restrictions": ["None"],
                    "goals": ["Digestive health", "Anti-inflammatory", "Energy optimization"],
                    "fasting_window": "14:10 Time-restricted",
                    "budget_level": "Moderate (balance cost/quality)",
                    "prep_style": "Daily fresh cooking",
                    "calorie_tier": "Moderate (1,600-2,200 kcal) - Maintenance",
                    "preferences": "Plant-forward, mindful eating with seasonal, local ingredients",
                    "food_relationship": "Food as medicine and spiritual nourishment",
                    "decision_style": "Intuitive eating with mindful awareness"
                },
                "mental_resilience": {
                    "diet_type": "Mediterranean",
                    "meals_per_day": "3 meals (standard)",
                    "cooking_time": "Moderate (15-45 mins)",
                    "restrictions": ["None"],
                    "goals": ["Cognitive performance", "Anti-inflammatory", "Energy optimization"],
                    "fasting_window": "16:8 Intermittent Fasting",
                    "budget_level": "Moderate (balance cost/quality)",
                    "prep_style": "Hybrid (some prep)",
                    "calorie_tier": "Moderate (1,600-2,200 kcal) - Maintenance",
                    "preferences": "Brain-boosting nutrients, steady energy, anti-inflammatory foods",
                    "food_relationship": "Precise nutrition and measurable results",
                    "decision_style": "Systems thinking about long-term impacts"
                },
                "planetary_stewardship": {
                    "diet_type": "Plant-Based",
                    "meals_per_day": "3 meals (standard)",
                    "cooking_time": "Extensive (45+ mins)",
                    "restrictions": ["None"],
                    "goals": ["Anti-inflammatory", "Longevity", "Digestive health"],
                    "fasting_window": "14:10 Time-restricted",
                    "budget_level": "Low (premium ingredients okay)",
                    "prep_style": "Daily fresh cooking",
                    "calorie_tier": "Moderate (1,600-2,200 kcal) - Maintenance",
                    "preferences": "Regenerative, locally-sourced, minimal environmental impact",
                    "food_relationship": "Understanding food systems and sustainability",
                    "decision_style": "Systems thinking about long-term impacts"
                },
                "default": {
                    "diet_type": "Omnivore",
                    "meals_per_day": "3 meals (standard)",
                    "cooking_time": "Moderate (15-45 mins)",
                    "restrictions": ["None"],
                    "goals": ["Energy optimization", "Digestive health"],
                    "fasting_window": "16:8 Intermittent Fasting",
                    "budget_level": "Moderate (balance cost/quality)",
                    "prep_style": "Weekly batch prep",
                    "calorie_tier": "Moderate (1,600-2,200 kcal) - Maintenance",
                    "preferences": "Balanced approach across all sovereignty domains",
                    "food_relationship": "Precise nutrition and measurable results",
                    "decision_style": "Based on data, macros, and proven science"
                }
            }
            
            quick_preferences = path_defaults.get(path, path_defaults["default"])
            st.session_state.meal_preferences = quick_preferences
            st.session_state.generate_meal_plan = True
            st.session_state.quick_plan_generated = True
            st.rerun()
    
    with quick_col2:
        if st.button("🎯 Optimize my cooking streak", key="optimize_cooking", use_container_width=True):
            cooking_streak = current_streaks.get("cooking", 0)
            streak_preferences = {
                "diet_type": "Omnivore",
                "meals_per_day": "4 meals (frequent)",
                "cooking_time": "Minimal (< 15 mins)",
                "restrictions": ["None"],
                "goals": ["Time efficiency", "Energy optimization"],
                "fasting_window": "No restrictions",
                "budget_level": "Moderate (balance cost/quality)",
                "prep_style": "Weekly batch prep",
                "calorie_tier": "Moderate (1,600-2,200 kcal) - Maintenance",
                "preferences": f"Quick, easy meals to maintain my {cooking_streak}-day cooking streak. Focus on simple prep and consistent habits.",
                "food_relationship": "Precise nutrition and measurable results",
                "decision_style": "Based on data, macros, and proven science"
            }
            
            st.session_state.meal_preferences = streak_preferences
            st.session_state.generate_meal_plan = True
            st.session_state.quick_plan_generated = True
            st.rerun()
    
    with quick_col3:
        if st.button("⚡ High-performance nutrition", key="performance_nutrition", use_container_width=True):
            performance_preferences = {
                "diet_type": "Omnivore",
                "meals_per_day": "5+ meals (athlete/bulk)",
                "cooking_time": "Weekend warrior (batch prep)",
                "restrictions": ["None"],
                "goals": ["Muscle gain", "Athletic performance", "Cognitive performance"],
                "fasting_window": "No restrictions",
                "budget_level": "Low (premium ingredients okay)",
                "prep_style": "Weekly batch prep",
                "calorie_tier": "Very High (2,800-3,500+ kcal) - Athlete/bulking",
                "preferences": "Maximum performance nutrition based on Huberman and Cavaliere principles. High protein, optimized timing.",
                "food_relationship": "Precise nutrition and measurable results",
                "decision_style": "Based on data, macros, and proven science"
            }
            
            st.session_state.meal_preferences = performance_preferences
            st.session_state.generate_meal_plan = True
            st.session_state.quick_plan_generated = True
            st.rerun()

    # Show if quick plan was generated
    if st.session_state.get("quick_plan_generated", False):
        st.success("🚀 Quick meal plan generated! Check below for your personalized nutrition plan.")
        del st.session_state["quick_plan_generated"]

    # COLLAPSIBLE ADVANCED FORM
    with st.expander("🔧 Advanced Meal Plan Options", expanded=False):
        st.markdown("### 📋 Custom Meal Plan Preferences")
        
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
                
                # Developmental assessment questions
                st.markdown("### 🧠 Food Philosophy")
                food_relationship = st.selectbox("What's most important to you about food?", [
                    "Precise nutrition and measurable results",
                    "Connection to nature and seasonal eating", 
                    "Understanding food systems and sustainability",
                    "Food as medicine and spiritual nourishment"
                ])
                
                decision_style = st.selectbox("How do you prefer to make food choices?", [
                    "Based on data, macros, and proven science",
                    "Intuitive eating with mindful awareness",
                    "Systems thinking about long-term impacts", 
                    "Holistic integration of body, mind, and spirit"
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
            
            submitted = st.form_submit_button("🚀 Generate Custom Meal Plan", type="primary")

        if submitted:
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
                "preferences": preferences,
                "food_relationship": food_relationship,
                "decision_style": decision_style
            }
            
            st.session_state.meal_preferences = user_preferences
            st.session_state.generate_meal_plan = True

    # Generate meal plan (from quick buttons or form)
    if st.session_state.get("generate_meal_plan", False):
        user_preferences = st.session_state.get("meal_preferences", {})
        
        if "current_meal_plan" not in st.session_state or st.session_state.get("meal_preferences_hash") != hash(str(user_preferences)):
            
            # Show consciousness level detection
            food_philosophy_mapping = {
                "Precise nutrition and measurable results": "Orange",
                "Connection to nature and seasonal eating": "Green", 
                "Understanding food systems and sustainability": "Teal",
                "Food as medicine and spiritual nourishment": "Turquoise"
            }
            
            decision_mapping = {
                "Based on data, macros, and proven science": "Orange",
                "Intuitive eating with mindful awareness": "Green",
                "Systems thinking about long-term impacts": "Teal",
                "Holistic integration of body, mind, and spirit": "Turquoise"
            }
            
            food_consciousness = food_philosophy_mapping.get(user_preferences.get('food_relationship', ''), 'Orange')
            decision_consciousness = decision_mapping.get(user_preferences.get('decision_style', ''), 'Orange')
            
            consciousness_levels = ['Orange', 'Green', 'Teal', 'Turquoise']
            primary_level = consciousness_levels[max(
                consciousness_levels.index(food_consciousness),
                consciousness_levels.index(decision_consciousness)
            )]
            
            st.markdown(f"""
            <div class="consciousness-indicator">
                🧠 Nutritional Approach: {primary_level} Level
            </div>
            """, unsafe_allow_html=True)
            
            with st.spinner("🧠 AI Chef is crafting your consciousness-aligned meal plan..."):
                meal_plan = meal_agent.generate_meal_plan(user_meal_data, user_preferences)
                
                if meal_plan:
                    st.session_state.current_meal_plan = meal_plan
                    st.session_state.meal_preferences_hash = hash(str(user_preferences))
                    st.session_state.consciousness_level = primary_level
                else:
                    st.error("❌ Failed to generate meal plan. Please try again.")
                    st.session_state.generate_meal_plan = False
                    st.stop()
        
        # Display the meal plan
        meal_plan = st.session_state.get("current_meal_plan")
        consciousness_level = st.session_state.get("consciousness_level", "Orange")
        
        if meal_plan:
            display_meal_plan(meal_plan, user_preferences, consciousness_level)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 20px; color: #6b7280;">
        <p>🛡️ <strong>Nutrition is the foundation of sovereignty.</strong></p>
        <p><em>Every meal you cook builds your independence from industrial food systems.</em></p>
    </div>
    """, unsafe_allow_html=True)

def display_meal_plan(meal_plan, preferences, consciousness_level):
    """Display the generated meal plan with consciousness level integration"""
    
    st.markdown("---")
    st.markdown("## 🍽️ Your Sovereignty Meal Plan")
    
    # Show consciousness level
    consciousness_descriptions = {
        "Orange": "Optimization & Performance Focused",
        "Green": "Holistic & Environmentally Conscious",
        "Teal": "Systems-Thinking & Regenerative",
        "Turquoise": "Transpersonal & Spiritually Integrated"
    }
    
    st.markdown(f"""
    <div class="consciousness-indicator">
        🧠 Nutritional Consciousness: {consciousness_level} - {consciousness_descriptions.get(consciousness_level, "Integrated Approach")}
    </div>
    """, unsafe_allow_html=True)
    
    # Overview section
    if "meal_plan" in meal_plan:
        overview = meal_plan["meal_plan"]
        
        st.markdown("### 📖 Plan Overview")
        st.markdown(f"""
        <div class="nutrition-insight">
            <h4>🛡️ Sovereignty Alignment</h4>
            <p><strong>Philosophy:</strong> {overview.get('overview', 'Custom sovereignty nutrition approach')}</p>
            <p><strong>Structure:</strong> {overview.get('daily_structure', 'Optimized for your preferences')}</p>
            <p><strong>Consciousness Approach:</strong> {overview.get('consciousness_approach', 'Aligned with your developmental level')}</p>
        </div>
        """, unsafe_allow_html=True)
        
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
        
        st.markdown(f"""
        <div class="nutrition-insight">
            <h4>🎯 Path-Specific Benefits</h4>
            <p><strong>Benefits:</strong> {optimization.get('specific_benefits', 'Optimized for your sovereignty journey')}</p>
            <p><strong>Habit Integration:</strong> {optimization.get('habit_integration', 'Seamlessly integrates with your current habits')}</p>
            <p><strong>Progression:</strong> {optimization.get('progression_suggestions', 'Strategies for advancing your nutrition sovereignty')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Download options with consciousness level in filename
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
    
    # Enhanced download functions with consciousness level
    def create_shopping_download():
        df_shopping = pd.DataFrame([(k, str(v)) for k, v in shopping_data.items()], 
                                 columns=["Category", "Items"])
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df_shopping.to_excel(writer, index=False, sheet_name="Shopping List")
        buffer.seek(0)
        return buffer.getvalue()
    
    def create_meal_download():
        df_meals = pd.DataFrame(meal_data)
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df_meals.to_excel(writer, index=False, sheet_name="Meal Plan")
        buffer.seek(0)
        return buffer.getvalue()
    
    def create_full_download():
        plan_summary = {
            "Plan Overview": meal_plan.get("meal_plan", {}).get("overview", ""),
            "Consciousness Level": consciousness_level,
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
            file_name=f"sovereignty_shopping_{consciousness_level.lower()}_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        st.download_button(
            label="🍽️ Download Meal Plan", 
            data=create_meal_download(),
            file_name=f"sovereignty_meals_{consciousness_level.lower()}_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col3:
        st.download_button(
            label="📊 Download Full Plan",
            data=create_full_download(),
            file_name=f"complete_sovereignty_plan_{consciousness_level.lower()}_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

if __name__ == "__main__":
    main()