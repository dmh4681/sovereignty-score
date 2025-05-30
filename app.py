import streamlit as st

st.set_page_config(
    page_title="Sovereignty Score Tracker",
    page_icon="🏰",
    layout="wide"
)

import pandas as pd
import requests
import os, json
from datetime import datetime
from tracker.scoring import calculate_daily_score
import logging
from utils import get_current_btc_price, usd_to_sats
from db import get_db_connection, init_db

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ── Setup ──────────────────────────────────────────────────────────────────────
BASE = os.path.dirname(__file__)
logger.debug(f"Base directory: {BASE}")

# Load path-definitions with error handling
try:
    paths_file = os.path.join(BASE, "config", "paths.json")
    logger.debug(f"Loading paths from: {paths_file}")
    with open(paths_file, 'r', encoding='utf-8') as f:
        ALL_PATHS = json.load(f)
    logger.debug(f"Loaded paths: {list(ALL_PATHS.keys())}")
except Exception as e:
    logger.error(f"Error loading paths configuration: {str(e)}")
    st.error(f"Critical Error: Could not load paths configuration. Please check config/paths.json")
    st.stop()

# ── Utility Functions ──────────────────────────────────────────────────────────
def validate_form_data(data):
    """Validate form data before processing"""
    errors = []
    
    # Check for negative values where they don't make sense
    if data.get('home_cooked_meals', 0) < 0:
        errors.append("Home cooked meals cannot be negative")
    if data.get('exercise_minutes', 0) < 0:
        errors.append("Exercise minutes cannot be negative")
    if data.get('btc_usd', 0) < 0:
        errors.append("Bitcoin investment cannot be negative")
    
    # Check for reasonable upper bounds
    if data.get('home_cooked_meals', 0) > 10:
        errors.append("More than 10 meals per day seems unrealistic")
    if data.get('exercise_minutes', 0) > 500:
        errors.append("More than 8 hours of exercise seems unrealistic")
    
    return errors

def safe_calculate_score(data, path):
    """Safely calculate score with error handling"""
    try:
        score = calculate_daily_score(data, path=path)
        # Ensure score is within valid range
        score = max(0, min(100, int(round(score))))
        return score, None
    except Exception as e:
        logger.error(f"Error calculating score: {str(e)}")
        return 0, str(e)

# ── Handle Login via Query-Params ─────────────────────────────────────────────
all_params = dict(st.query_params)
logger.debug(f"All query parameters: {all_params}")

username = st.query_params.get("username", None)
path = st.query_params.get("path", None)

# Store in session state if we got it from query params
if username:
    st.session_state.username = username
if path and path in ALL_PATHS:  # Validate path exists
    st.session_state.path = path

# Use session state if query params not available
username = username or st.session_state.get("username", None)
path = path or st.session_state.get("path", None)

logger.debug(f"Login params - username: {username}, path: {path}")

# Validate path exists in configuration
if path and path not in ALL_PATHS:
    logger.warning(f"Invalid path {path} specified")
    st.error(f"❌ Invalid path: {path}. Please contact support.")
    st.stop()

# Custom login handler inside the app
if not username or not path:
    st.title("🏰 Sovereignty Score Login")
    st.warning("Please log in to access your tracker.")

    with st.form("login_form"):
        login_username = st.text_input("Username")
        login_password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Log In")

    if submit:
        login_payload = {
            "username": login_username,
            "password": login_password
        }
        try:
            response = requests.post("http://localhost:5002/login", json=login_payload)
            if response.status_code == 200:
                result = response.json()
                st.session_state.username = result["username"]
                st.session_state.path = result["path"]
                st.success("✅ Login successful! Loading your tracker...")
                st.rerun()
            else:
                error_msg = response.json().get("message", "Login failed.")
                st.error(f"❌ {error_msg}")
        except Exception as e:
            st.error(f"Login error: {str(e)}")
    st.stop()

# Verify user exists and path is valid
try:
    logger.debug(f"Verifying user {username} with path {path}")
    with get_db_connection() as conn:
        user = conn.execute(
            "SELECT username, path FROM users WHERE username = ? AND path = ?",
            [username, path]
        ).fetchone()
        
        if not user:
            logger.warning(f"User {username} with path {path} not found")
            st.error("❌ User not found or invalid path. Please register first.")
            st.markdown("[Return to Landing Page](https://dmh4681.github.io/sovereignty-score/)")
            st.stop()
            
        logger.debug(f"User verified: {user}")
except Exception as e:
    logger.error(f"Database error during user verification: {str(e)}")
    st.error(f"❌ Database error: {str(e)}")
    st.stop()

# ── Build the Habit Tracker UI ────────────────────────────────────────────────
st.title("🏰 Sovereignty Score Tracker")
st.sidebar.markdown(f"### Logged in as {username}")
st.sidebar.markdown(f"### Path: {path.replace('_',' ').title()}")

# Show how this path is scored
try:
    cfg = ALL_PATHS[path]
    
    # Display path description
    st.sidebar.markdown(f"**{cfg.get('description', '')}**")
    
    # Create a more compact metrics display
    st.sidebar.markdown("### 📊 Scoring Guide")
    st.sidebar.markdown("""
        <style>
        .small-text {
            font-size: 0.9em;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Group metrics by category
    categories = {
        "Physical": ["home_cooked_meals", "no_junk_food", "exercise_minutes", "strength_training"],
        "Financial": ["no_spending", "invested_bitcoin"],
        "Mental / Spiritual": ["meditation", "gratitude", "read_or_learned"],
        "Environmental": ["environmental_action"]
    }
    
    for category, metrics in categories.items():
        st.sidebar.markdown(f"#### {category}")
        for metric in metrics:
            if metric in cfg:
                value = cfg[metric]
                if isinstance(value, dict):
                    points = value.get('points_per_unit', 0)
                    max_units = value.get('max_units', 1)
                    max_points = points * max_units
                    st.sidebar.markdown(
                        f'<div class="small-text">'
                        f"- {metric.replace('_', ' ').title()}\n"
                        f"  {points} pts × {max_units} = {max_points} max"
                        f'</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.sidebar.markdown(
                        f'<div class="small-text">'
                        f"- {metric.replace('_', ' ').title()}: {value} pts"
                        f'</div>',
                        unsafe_allow_html=True
                    )
    
except Exception as e:
    logger.error(f"Error loading path configuration: {str(e)}")
    st.error(f"Error loading path configuration: {str(e)}")

# ── Main Form ──────────────────────────────────────────────────────────────────
with st.form("tracker_form"):
    st.markdown("### Today's Activities")
    
    # Physical activities
    st.markdown("#### 🏋️ Physical")
    meals = st.number_input("Home-cooked meals", min_value=0, max_value=10, value=0, 
                           help="How many meals did you cook at home today?")
    no_junk = st.checkbox("No junk food today?", 
                         help="Check if you avoided junk food completely today")
    mins = st.number_input("Exercise minutes", min_value=0, max_value=300, value=0,
                          help="Total minutes of exercise today")
    lift = st.checkbox("Strength training?", 
                      help="Did you do any strength/resistance training?")
    
    # Financial activities
    st.markdown("#### 💰 Financial")
    spend = st.checkbox("No discretionary spending?",
                       help="Did you avoid unnecessary purchases today?")
    
    # Bitcoin investment with improved UX
    btc_usd = st.number_input("Bitcoin investment today (USD)", min_value=0.0, step=1.0, value=0.0,
                             help="How much did you invest in Bitcoin today?")
    
    # Show current BTC price and sats calculation
    current_btc_price = get_current_btc_price()
    if current_btc_price and btc_usd > 0:
        btc_sats = usd_to_sats(btc_usd, current_btc_price)
        st.info(f"💡 ${btc_usd:.2f} = {btc_sats:,} sats (@ ${current_btc_price:,.0f}/BTC)")
    else:
        btc_sats = 0
        if btc_usd > 0:
            st.warning("⚠️ Could not fetch current BTC price for sats conversion")
    
    btc = btc_usd > 0  # Set bitcoin investment flag
    
    # Mental/Spiritual activities
    st.markdown("#### 🧠 Mental & Spiritual")
    med = st.checkbox("Meditated?", 
                     help="Did you practice meditation or mindfulness?")
    grat = st.checkbox("Gratitude practice?",
                      help="Did you practice gratitude today?")
    learn = st.checkbox("Read or learned something new?",
                       help="Did you read, study, or learn something today?")
    
    # Environmental
    st.markdown("#### 🌍 Environmental")
    env = st.checkbox("Environmentally friendly action?",
                     help="Did you take action to help the environment today?")
    
    submitted = st.form_submit_button("Submit & Save", type="primary")

# ── Process Form Submission ────────────────────────────────────────────────────
if submitted:
    # Create data structure for scoring
    data = {
        "home_cooked_meals": meals,
        "junk_food": not no_junk,  # Invert: True means ate junk food
        "exercise_minutes": mins,
        "strength_training": lift,
        "no_spending": spend,
        "invested_bitcoin": btc,
        "btc_usd": float(btc_usd),
        "btc_sats": int(btc_sats),
        "meditation": med,
        "gratitude": grat,
        "read_or_learned": learn,
        "environmental_action": env
    }
    
    # Validate data
    validation_errors = validate_form_data(data)
    if validation_errors:
        st.error("❌ Please fix the following issues:")
        for error in validation_errors:
            st.error(f"• {error}")
    else:
        # Calculate score safely
        score, score_error = safe_calculate_score(data, path)
        
        if score_error:
            st.error(f"❌ Error calculating score: {score_error}")
        else:
            # Save to database using named columns (FIXED!)
            try:
                with get_db_connection() as conn:
                    conn.execute("""
                        INSERT INTO sovereignty (
                            timestamp, username, path,
                            home_cooked_meals, junk_food, exercise_minutes, strength_training,
                            no_spending, invested_bitcoin, btc_usd, btc_sats,
                            meditation, gratitude, read_or_learned, environmental_action, score
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, [
                        datetime.utcnow(), username, path,
                        meals, not no_junk, mins, lift,
                        spend, btc, float(btc_usd), int(btc_sats),
                        med, grat, learn, env, int(score)
                    ])
                
                st.success(f"💪 Your score: {score}/100")
                
                # Show score breakdown if it's not the maximum
                if score < cfg.get('max_score', 100):
                    with st.expander("🔍 See score breakdown"):
                        st.json(data)
                        
            except Exception as e:
                logger.error(f"Database error saving data: {str(e)}")
                st.error(f"❌ Error saving data: {str(e)}")

# ── Show History ───────────────────────────────────────────────────────────────
try:
    with get_db_connection() as conn:
        # Use explicit column names in SELECT to match database schema
        hist = conn.execute("""
            SELECT 
                timestamp, path, score,
                home_cooked_meals, junk_food, exercise_minutes, strength_training,
                no_spending, invested_bitcoin, btc_usd, btc_sats,
                meditation, gratitude, read_or_learned, environmental_action
            FROM sovereignty
            WHERE username = ?
            ORDER BY timestamp DESC
            LIMIT 50
        """, [username]).df()

    st.subheader("📜 Your Recent History")
    if hist.empty:
        st.info("📘 No entries yet. Submit your first day above to get started!")
    else:
        # Format the dataframe for better display
        if not hist.empty:
            # Convert timestamp to readable format
            hist['timestamp'] = pd.to_datetime(hist['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
            
            # Rename columns for display
            display_columns = {
                'timestamp': 'Date',
                'score': 'Score',
                'path': 'Path',
                'home_cooked_meals': 'Meals',
                'junk_food': 'Ate Junk',
                'exercise_minutes': 'Exercise (min)',
                'strength_training': 'Strength',
                'no_spending': 'No Spending',
                'invested_bitcoin': 'Stacked Sats',
                'btc_usd': 'BTC ($)',
                'btc_sats': 'Sats',
                'meditation': 'Meditation',
                'gratitude': 'Gratitude',
                'read_or_learned': 'Learning',
                'environmental_action': 'Environmental'
            }
            
            hist = hist.rename(columns=display_columns)
            
            # Show summary stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Average Score", f"{hist['Score'].mean():.1f}")
            with col2:
                st.metric("Total Days", len(hist))
            with col3:
                st.metric("Total Sats", f"{hist['Sats'].sum():,}")
            with col4:
                st.metric("Total BTC Invested", f"${hist['BTC ($)'].sum():.2f}")
            
            # Display the data
            st.dataframe(hist, use_container_width=True, hide_index=True)
            
except Exception as e:
    logger.error(f"Error loading history: {str(e)}")
    st.error(f"❌ Error loading history: {str(e)}")
    st.info("If this persists, you may need to reset your data due to database corruption.")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("🛡️ **Sovereignty is the new health plan.** Track daily, build consistently, own your future.")