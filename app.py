import streamlit as st
import pandas as pd
import os, json
from datetime import datetime
from tracker.scoring import calculate_daily_score
import logging
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
logger.debug(f"Login params - username: {username}, path: {path}")

# If no login parameters, show a friendly message
if not username or not path:
    logger.warning("No login parameters provided")
    st.title("🏰 Welcome to Sovereignty Score")
    st.info("Please log in through the landing page to access your tracker.")
    st.markdown("[Return to Landing Page](https://dmh4681.github.io/sovereignty-score/)")
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
    
    # Create a DataFrame for the metrics
    metrics_data = []
    for metric, value in cfg.items():
        if metric not in ('description', 'max_score'):
            if isinstance(value, dict):
                points = value.get('points_per_unit', 0)
                max_units = value.get('max_units', 1)
                metrics_data.append({
                    'Metric': metric.replace('_', ' ').title(),
                    'Points Per Unit': points,
                    'Max Units': max_units,
                    'Max Points': points * max_units
                })
            else:
                metrics_data.append({
                    'Metric': metric.replace('_', ' ').title(),
                    'Points': value
                })
    
    metrics_df = pd.DataFrame(metrics_data)
    
    # Display the metrics table
    st.sidebar.dataframe(
        metrics_df,
        use_container_width=True,
        height=min(400, 32 * len(metrics_data) + 20)
    )
except Exception as e:
    logger.error(f"Error loading path configuration: {str(e)}")
    st.error(f"Error loading path configuration: {str(e)}")
    # Don't stop the app, just show the error and continue
    st.warning("Some features may be limited due to configuration issues.")

# Habit-logging form
with st.form("tracker_form"):
    meals = st.number_input("Home-cooked meals", min_value=0, max_value=10, value=0)
    junk  = st.checkbox("No junk food today?")
    mins  = st.number_input("Exercise minutes", min_value=0, max_value=300, value=0)
    lift  = st.checkbox("Strength training?")
    spend= st.checkbox("No discretionary spending?")
    btc  = st.checkbox("Invested in Bitcoin?")
    med  = st.checkbox("Meditated?")
    grat = st.checkbox("Gratitude practice?")
    learn= st.checkbox("Read or learned something new?")
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
      "meditation":       med,
      "gratitude":        grat,
      "read_or_learned":  learn,
      "environmental_action":env
    }
    score = calculate_daily_score({**data, "path":path}, path=path)
    try:
        with get_db_connection() as conn:
            conn.execute("""
              INSERT INTO sovereignty VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?);
            """, [
              datetime.utcnow(), user[0], path,
              meals, not junk, mins, lift,
              spend, btc, med, grat,
              learn, env, score
            ])
        st.success(f"💪 Your score: {score}/100")
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")

# Show history
try:
    with get_db_connection() as conn:
        hist = conn.execute("""
          SELECT timestamp, path, home_cooked_meals, junk_food,
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
        st.dataframe(hist, use_container_width=True)
except Exception as e:
    st.error(f"Error loading history: {str(e)}")
