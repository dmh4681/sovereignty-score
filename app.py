import os
import json
import duckdb
import streamlit as st
import pandas as pd
from datetime import datetime
from tracker.scoring import calculate_daily_score

# — Constants & Paths —
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(BASE_DIR, "data")
CONFIG_DIR  = os.path.join(BASE_DIR, "config")
DB_FILE     = os.path.join(DATA_DIR, "sovereignty.duckdb")
PATHS_FILE  = os.path.join(CONFIG_DIR, "paths.json")
USERS_SQL   = os.path.join(CONFIG_DIR, "create_users_table.sql")

# — Ensure data directory exists —
os.makedirs(DATA_DIR, exist_ok=True)

# — Load scoring definitions —
with open(PATHS_FILE, "r", encoding="utf-8") as f:
    ALL_PATHS = json.load(f)

# — Connect to DuckDB & initialize schema —
con = duckdb.connect(DB_FILE)

# 1) Users table
if os.path.isfile(USERS_SQL):
    with open(USERS_SQL, "r") as f:
        con.execute(f.read())

# 2) Sovereignty entries table
con.execute("""
CREATE TABLE IF NOT EXISTS sovereignty (
    timestamp            TIMESTAMP,
    username             VARCHAR,
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

# — Streamlit UI — 
st.set_page_config(page_title="Sovereignty Score Tracker")
st.title("🏰 Sovereignty Score Tracker")
st.markdown("Track habits, get scored, and visualize your sovereign progress.")

# — Sidebar: Username & Path selection —
st.sidebar.title("User & Path")

username = st.sidebar.text_input("Username", max_chars=30).strip()
path_labels = list(ALL_PATHS.keys())
path_map    = {label: label for label in path_labels}  # labels == keys

default_path = st.query_params.get("path", [None])[0] or "default"
if default_path not in path_map:
    default_path = "default"

if "path_choice" not in st.session_state:
    st.session_state.path_choice = default_path

selected_path = st.sidebar.selectbox(
    "Choose your Path",
    options=path_labels,
    index=path_labels.index(st.session_state.path_choice),
    key="path_choice"
)

# — Sidebar: Show how this Path is scored —
with st.sidebar.expander("ℹ️ Path Breakdown", expanded=False):
    cfg = ALL_PATHS[selected_path]
    desc = cfg.get("description", "")
    if desc:
        st.markdown(f"**{selected_path.replace('_',' ').title()}**")
        st.markdown(f"*{desc}*")

    flat = {}
    for metric, val in cfg.items():
        if metric in ("description", "max_score"): 
            continue
        if isinstance(val, dict):
            for subk, subv in val.items():
                flat[f"{metric}.{subk}"] = subv
        else:
            flat[metric] = val

    df_breakdown = pd.DataFrame.from_records(
        list(flat.items()), columns=["Metric", "Value"]
    )
    st.dataframe(df_breakdown, use_container_width=True, height=min(300, 32*len(df_breakdown)+20))

# — Stop if no username —
if not username:
    st.warning("⚠️ Enter a username above to continue.")
    st.stop()

# — Form for daily inputs —
st.subheader(f"Hello, {username} 👋")
with st.form("daily_form"):
    meals = st.number_input("Home-cooked meals", 0, 10, 0)
    junk  = st.checkbox("No junk food today?")
    mins  = st.number_input("Exercise minutes", 0, 300, 0)
    lift  = st.checkbox("Strength training?")
    spend = st.checkbox("No discretionary spending?")
    btc   = st.checkbox("Invested in Bitcoin?")
    med   = st.checkbox("Meditated?")
    grat  = st.checkbox("Gratitude practice?")
    learn = st.checkbox("Read or learned something new?")
    env   = st.checkbox("Took environmentally friendly action today?")
    submitted = st.form_submit_button("Submit & Save")

# — On submit, compute score & insert —
if submitted:
    data = {
        "username":             username,
        "path":                 selected_path,
        "home_cooked_meals":    meals,
        "junk_food":            not junk,
        "exercise_minutes":     mins,
        "strength_training":    lift,
        "no_spending":          spend,
        "invested_bitcoin":     btc,
        "meditation":           med,
        "gratitude":            grat,
        "read_or_learned":      learn,
        "environmental_action": env,
    }
    score = calculate_daily_score(data, path=selected_path)
    st.success(f"💪 Your Sovereignty Score: **{score} / 100**")
    st.info(f"Path: **{selected_path.replace('_',' ').title()}**")

    con.execute("""
    INSERT INTO sovereignty VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, [
        datetime.now(),
        data["username"],
        data["path"],
        data["home_cooked_meals"],
        data["junk_food"],
        data["exercise_minutes"],
        data["strength_training"],
        data["no_spending"],
        data["invested_bitcoin"],
        data["meditation"],
        data["gratitude"],
        data["read_or_learned"],
        data["environmental_action"],
        score
    ])

# — Display History —
st.subheader("📜 Your History")
df_hist = con.execute(
    """
    SELECT timestamp, path, home_cooked_meals, junk_food,
           exercise_minutes, strength_training, no_spending,
           invested_bitcoin, meditation, gratitude,
           read_or_learned, environmental_action, score
      FROM sovereignty
     WHERE username = ?
  ORDER BY timestamp DESC
    """,
    [username]
).df()

if df_hist.empty:
    st.info("📘 No entries yet. Submit above to get started.")
else:
    st.dataframe(df_hist, use_container_width=True)
