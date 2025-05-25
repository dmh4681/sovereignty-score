import streamlit as st
import pandas as pd
import duckdb, os, json
from datetime import datetime
from tracker.scoring import calculate_daily_score

# — Paths & setup —
BASE       = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Load all scoring paths + descriptions
PATHS_FILE = os.path.join(BASE, "config", "paths.json")
with open(PATHS_FILE, "r", encoding="utf-8") as f:
    ALL_PATHS = json.load(f)

# — DuckDB setup —
DB_FILE = os.path.join(DATA_DIR, "sovereignty.duckdb")
con = duckdb.connect(DB_FILE)
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

# — Page title & sidebar —
st.title("🏰 Sovereignty Score Tracker")
st.markdown("Track your sovereign choices. Enter your habits, get a score, and visualize your progress.")

st.sidebar.title("User & Path")
username = st.sidebar.text_input("Enter your username:", max_chars=30)

path_options = {
    "Default (Balanced)":    "default",
    "Financial Path":        "financial_path",
    "Mental Resilience":     "mental_resilience",
    "Physical Optimization": "physical_optimization",
    "Spiritual Growth":      "spiritual_growth",
    "Planetary Stewardship": "planetary_stewardship",
}

# Pre-select via ?path=… in URL
# new, correct:
default_path = st.query_params.get("path", [None])[0]
reverse_map  = {v:k for k,v in path_options.items()}
default_label = reverse_map.get(default_path, "Default (Balanced)")

if "selected_label" not in st.session_state:
    st.session_state.selected_label = default_label

selected_label = st.sidebar.selectbox(
    "Scoring Profile",
    list(path_options.keys()),
    key="selected_label"
)
selected_path = path_options[selected_label]

# Show description + metric breakdown
with st.sidebar.expander("ℹ️ How this Path is Scored", expanded=False):
    desc = ALL_PATHS[selected_path].get("description","")
    st.markdown(f"**{selected_label}**")
    if desc:
        st.markdown(f"*{desc}*")
    # flatten metrics
    flat = {}
    for metric,val in ALL_PATHS[selected_path].items():
        if metric=="description": continue
        if isinstance(val,dict):
            for subk,subv in val.items():
                flat[f"{metric}.{subk}"] = subv
        else:
            flat[metric] = val
    df_scoring = pd.DataFrame.from_records(
        list(flat.items()), columns=["Metric","Value"]
    )
    st.dataframe(df_scoring, use_container_width=True, height=min(400,32*len(df_scoring)+20))

# — Main UI —
if not username:
    st.warning("⚠️ Please enter your username in the sidebar to begin.")
    st.stop()

st.subheader(f"Hello, {username} 👋")

# Input form
with st.form("tracker_form"):
    meals = st.number_input("Home-cooked meals", min_value=0, max_value=10, value=0)
    junk  = st.checkbox("No junk food today?")
    mins  = st.number_input("Exercise minutes", min_value=0, max_value=300, value=0)
    lift  = st.checkbox("Strength training?")
    spend = st.checkbox("No discretionary spending?")
    btc   = st.checkbox("Invested in Bitcoin?")
    med   = st.checkbox("Meditated?")
    grat  = st.checkbox("Gratitude practice?")
    learn = st.checkbox("Read or learned something new?")
    env   = st.checkbox("Took environmentally friendly action today?")
    submitted = st.form_submit_button("Submit & Save")

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
    st.success(f"💪 Sovereignty Score: **{score} / 100**")
    st.info(f"Scoring Path: **{selected_label}**")

    # write into DuckDB
    con.execute("""
      INSERT INTO sovereignty VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?);
    """, [
      datetime.now(), data["username"], data["path"],
      data["home_cooked_meals"], data["junk_food"],
      data["exercise_minutes"], data["strength_training"],
      data["no_spending"], data["invested_bitcoin"],
      data["meditation"], data["gratitude"],
      data["read_or_learned"], data["environmental_action"],
      score
    ])

# Show history
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
    st.info("📘 You have no entries yet. Submit above to get started.")
else:
    st.dataframe(df_hist, use_container_width=True)
