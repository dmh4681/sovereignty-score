import streamlit as st
import pandas as pd
import os, json
from datetime import datetime
from tracker.scoring import calculate_daily_score
import logging
from db import get_db_connection, init_db

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Setup ──────────────────────────────────────────────────────────────────────
BASE = os.path.dirname(__file__)

# Load path-definitions
try:
    with open(os.path.join(BASE, "config", "paths.json")) as f:
        ALL_PATHS = json.load(f)
except Exception as e:
    st.error(f"Error loading paths configuration: {str(e)}")
    st.stop()

# ── Handle Login via Query-Params ─────────────────────────────────────────────
username = st.query_params.get("username", None)
path = st.query_params.get("path", None)

# If no login parameters, show a friendly message
if not username or not path:
    st.title("🏰 Welcome to Sovereignty Score")
    st.info("Please log in through the landing page to access your tracker.")
    st.markdown("[Return to Landing Page](https://dmh4681.github.io/sovereignty-score/)")
    st.stop()

# Verify user exists and path is valid
try:
    with get_db_connection() as conn:
        user = conn.execute(
            "SELECT username, path FROM users WHERE username = ? AND path = ?",
            [username, path]
        ).fetchone()
        
        if not user:
            st.error("❌ Invalid login credentials. Please try logging in again.")
            st.markdown("[Return to Landing Page](https://dmh4681.github.io/sovereignty-score/)")
            st.stop()
except Exception as e:
    st.error(f"❌ Database error: {str(e)}")
    st.stop()

# ── Build the Habit Tracker UI ────────────────────────────────────────────────
st.title("🏰 Sovereignty Score Tracker")
st.sidebar.markdown(f"### Logged in as {username}")
st.sidebar.markdown(f"### Path: {path.replace('_',' ').title()}")

# Show how this path is scored
try:
    cfg = ALL_PATHS[path]
    flat = {}
    for k,v in cfg.items():
        if k in ("description","max_score"): continue
        if isinstance(v, dict):
            for subk,subv in v.items():
                flat[f"{k}.{subk}"] = subv
        else:
            flat[k] = v
    st.sidebar.markdown(f"**{cfg.get('description','')}**")
    st.sidebar.dataframe(
        pd.DataFrame.from_records(flat.items(),columns=["Metric","Value"]),
        use_container_width=True, height=min(400,32*len(flat)+20)
    )
except Exception as e:
    st.error(f"Error loading path configuration: {str(e)}")
    st.stop()

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
           WHERE email = ?
        ORDER BY timestamp DESC
        """,[user[0]]).df()

    st.subheader("📜 Your History")
    if hist.empty:
        st.info("📘 No entries yet; submit above to get started.")
    else:
        st.dataframe(hist, use_container_width=True)
except Exception as e:
    st.error(f"Error loading history: {str(e)}")
