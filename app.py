import streamlit as st
import pandas as pd
import duckdb, os, json, smtplib, bcrypt
from datetime import datetime
from tracker.scoring import calculate_daily_score

# ── Setup ──────────────────────────────────────────────────────────────────────
BASE     = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE, "data"); os.makedirs(DATA_DIR, exist_ok=True)
DB_FILE  = os.path.join(DATA_DIR, "sovereignty.duckdb")
con      = duckdb.connect(DB_FILE)

# Create users & sovereignty tables
con.execute("""
CREATE TABLE IF NOT EXISTS users (
    username    TEXT PRIMARY KEY,
    email       TEXT NOT NULL,
    password    TEXT NOT NULL,
    path        TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
con.execute("""
CREATE TABLE IF NOT EXISTS sovereignty (
  timestamp            TIMESTAMP,
  email                VARCHAR,
  path                 VARCHAR,
  home_cooked_meals    INTEGER,
  junk_food            BOOLEAN,
  exercise_minutes     INTEGER,
  strength_training    BOOLEAN,
  no_spending          BOOLEAN,
  invested_bitcoin     BOOLEAN,
  meditation           BOOLEAN,
  gratitude            BOOLEAN,
  read_or_learned      BOOLEAN,
  environmental_action BOOLEAN,
  score                INTEGER
);
""")

# Load path-definitions
with open(os.path.join(BASE, "config", "paths.json")) as f:
    ALL_PATHS = json.load(f)

# ── Handle Sign-Up via Query-Params ─────────────────────────────────────────────
qp       = st.experimental_get_query_params()  # or st.query_params in 1.32+
email    = qp.get("email", [None])[0]
username = qp.get("username", [None])[0]
path     = qp.get("path", [None])[0]

# If we have signup info and user not yet in DB, register & send welcome
if email and username and path:
    user_exists = con.execute(
      "SELECT 1 FROM users WHERE email = ? OR username = ?", [email, username]
    ).fetchone()
    if not user_exists:
        # Generate a temporary password for the user
        temp_password = "temp_" + os.urandom(8).hex()
        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(temp_password.encode("utf-8"), salt).decode("utf-8")
        
        con.execute(
          "INSERT INTO users (username, email, password, path) VALUES (?, ?, ?, ?)",
          [username, email, hashed_pw, path]
        )
        # *** send welcome email here (via your existing Mailgun/OpenAI script) ***
        # send_welcome(email, username, path)

# ── Authentication Guard ───────────────────────────────────────────────────────
if not email or not username:
    st.error("❌ You must arrive via the Landing Page sign-up form.")
    st.stop()

# ── Build the Habit Tracker UI ────────────────────────────────────────────────
st.title("🏰 Sovereignty Score Tracker")
st.sidebar.markdown(f"### Logged in as {username} ({email})")
st.sidebar.markdown(f"### Path: {path.replace('_',' ').title()}")

# Show how this path is scored
cfg  = ALL_PATHS[path]
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
    con.execute("""
      INSERT INTO sovereignty VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?);
    """, [
      datetime.utcnow(), email, path,
      meals, not junk, mins, lift,
      spend, btc, med, grat,
      learn, env, score
    ])
    st.success(f"💪 Your score: {score}/100")

# Show history
hist = con.execute("""
  SELECT timestamp, path, home_cooked_meals, junk_food,
         exercise_minutes, strength_training, no_spending,
         invested_bitcoin, meditation, gratitude,
         read_or_learned, environmental_action, score
    FROM sovereignty
   WHERE email = ?
ORDER BY timestamp DESC
""",[email]).df()

st.subheader("📜 Your History")
if hist.empty:
    st.info("📘 No entries yet; submit above to get started.")
else:
    st.dataframe(hist, use_container_width=True)
