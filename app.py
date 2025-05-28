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

# Load path-definitions
try:
    paths_file = os.path.join(BASE, "config", "paths.json")
    logger.debug(f"Loading paths from: {paths_file}")
    with open(paths_file) as f:
        ALL_PATHS = json.load(f)
    logger.debug(f"Loaded paths: {list(ALL_PATHS.keys())}")
except Exception as e:
    logger.error(f"Error loading paths configuration: {str(e)}")
    st.error(f"Error loading paths configuration: {str(e)}")
    st.stop()

# ── Handle Login via Query-Params ─────────────────────────────────────────────
# Debug all query parameters
all_params = dict(st.query_params)
logger.debug(f"All query parameters: {all_params}")

username = st.query_params.get("username", None)
path = st.query_params.get("path", None)

# Store in session state if we got it from query params
if username:
    st.session_state.username = username
if path:
    st.session_state.path = path

# Use session state if query params not available
username = username or st.session_state.get("username", None)
path = path or st.session_state.get("path", None)

logger.debug(f"Login params - username: {username}, path: {path}")

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
        # First check if the user exists
        user_check = conn.execute(
            "SELECT username FROM users WHERE username = ?",
            [username]
        ).fetchone()
        
        if not user_check:
            logger.warning(f"User {username} not found in database")
            st.error("❌ User not found. Please register first.")
            st.markdown("[Return to Landing Page](https://dmh4681.github.io/sovereignty-score/)")
            st.stop()
            
        # Then check if the path matches
        user = conn.execute(
            "SELECT username, path FROM users WHERE username = ? AND path = ?",
            [username, path]
        ).fetchone()
        
        if not user:
            logger.warning(f"Path {path} not valid for user {username}")
            st.error("❌ Invalid path for this user. Please try logging in again.")
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
    logger.debug(f"Loading configuration for path: {path}")
    if path not in ALL_PATHS:
        logger.error(f"Path {path} not found in configuration")
        st.error(f"❌ Invalid path configuration. Please contact support.")
        st.stop()
        
    cfg = ALL_PATHS[path]
    
    # Display path description
    st.sidebar.markdown(f"**{cfg.get('description', '')}**")
    
    # Create a more compact metrics display with smaller text
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
        "Physical": ["home_cooked_meals", "junk_food", "exercise_minutes", "strength_training"],
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
    # Don't stop the app, just show the error and continue
    st.warning("Some features may be limited due to configuration issues.")

# Place this *before* the form so the checkbox state persists and controls the rest
btc = st.checkbox("Stacked Sats?")

# Now the rest of your form
with st.form("tracker_form"):
    meals = st.number_input("Home-cooked meals", min_value=0, max_value=10, value=0)
    junk  = st.checkbox("No junk food today?")
    mins  = st.number_input("Exercise minutes", min_value=0, max_value=300, value=0)
    lift  = st.checkbox("Strength training?")
    spend = st.checkbox("No discretionary spending?")

    btc_usd = 0
    btc_sats = 0
    if btc:
        btc_usd = st.number_input("How much BTC did you stack today (in USD)?", min_value=0.0, step=1.0)
        current_btc_price = get_current_btc_price()
        if current_btc_price:
            btc_sats = usd_to_sats(btc_usd, current_btc_price)
            st.success(f"🟠 {btc_sats:,} sats stacked today at ${current_btc_price:,}/BTC")

    med  = st.checkbox("Meditated?")
    grat = st.checkbox("Gratitude practice?")
    learn = st.checkbox("Read or learned something new?")
    env  = st.checkbox("Took environmentally friendly action today?")
    submitted = st.form_submit_button("Submit & Save")


if submitted:
    data = {
      "home_cooked_meals": meals,
      "junk_food":        not junk,
      "exercise_minutes": mins,
      "strength_training":lift,
      "no_spending":      spend,
      "invested_bitcoin": btc,
      "btc_usd":        btc_usd,
      "btc_sats":       btc_sats,
      "meditation":       med,
      "gratitude":        grat,
      "read_or_learned":  learn,
      "environmental_action":env
    }
    score = calculate_daily_score({**data, "path":path}, path=path)
    try:
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO sovereignty VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);
                """, [
                datetime.utcnow(), user[0], path,
                meals, not junk, mins, lift,
                spend, btc, btc_usd, btc_sats,
                med, grat, learn, env, score
                ])
        st.success(f"💪 Your score: {score}/100")
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")

# Show history
try:
    with get_db_connection() as conn:
        hist = conn.execute("""
          SELECT timestamp, username, path, btc_usd, btc_sats, home_cooked_meals, junk_food,
                 exercise_minutes, strength_training, no_spending,
                 invested_bitcoin, meditation, gratitude,
                 read_or_learned, environmental_action, score
            FROM sovereignty
           WHERE username = ?
        ORDER BY timestamp DESC
        """,[user[0]]).df()

    st.subheader("📜 Your History")
    if hist.empty:
        st.info("📘 No entries yet; submit above to get started.")
    else:
        # Drop the username column from display since we already know who we are
        display_df = hist.drop(columns=['username'])
        st.dataframe(display_df, use_container_width=True)
except Exception as e:
    st.error(f"Error loading history: {str(e)}")
