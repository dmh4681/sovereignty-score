import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import duckdb, os, json
from datetime import datetime
from tracker.scoring import calculate_daily_score

# — Paths & setup —
BASE       = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Load all scoring paths
PATHS_FILE = os.path.join(BASE, "config", "paths.json")
with open(PATHS_FILE, "r", encoding="utf-8") as f:
    ALL_PATHS = json.load(f)

# — DuckDB setup —
DB_FILE = os.path.join(DATA_DIR, "sovereignty.duckdb")
# open or create
con = duckdb.connect(DB_FILE)
# create our single table if it doesn’t exist
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

# — Page title & instructions —
st.title("🏰 Sovereignty Score Tracker")
st.markdown("Track your sovereign choices. Enter your habits, get a score, and visualize your progress.")

# — Sidebar: Username + Path selection —
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

# — Pre-select via URL query ?path=… into session_state —
query_params = st.query_params
default_path = query_params.get("path", [None])[0] if query_params else None

# map the internal path‐key back to the user‐facing label
reverse_map = {v: k for k, v in path_options.items()}
default_label = reverse_map.get(default_path, "Default (Balanced)")

# only initialize once, so session_state sticks across reruns
if "selected_label" not in st.session_state:
    st.session_state.selected_label = default_label

# now bind the selectbox to that session_state key
selected_label = st.sidebar.selectbox(
    "Scoring Profile",
    list(path_options.keys()),
    key="selected_label"
)
selected_path = path_options[selected_label]


# Sidebar breakdown
with st.sidebar.expander("ℹ️ How this Path is Scored", expanded=False):
    # 1) Print the human‐readable description once
    desc = ALL_PATHS[selected_path].get("description", "")
    if desc:
        st.markdown(f"**Profile:** {selected_label}")
        st.markdown(f"*{desc}*")
    else:
        st.markdown(f"**Profile:** {selected_label}")
    
    # 2) Build the flat metric→value table
    cfg = dict(ALL_PATHS[selected_path])          # take a shallow copy
    cfg.pop("description", None)                  # remove the narrative
    flat = {}
    for metric, val in cfg.items():
        if isinstance(val, dict):
            for subk, subv in val.items():
                flat[f"{metric}.{subk}"] = subv
        else:
            flat[metric] = val
    df_scoring = pd.DataFrame.from_records(
        list(flat.items()), columns=["Metric", "Value"]
    )

    # 3) Render as a native Streamlit DataFrame
    #    - adjust height so it doesn't take the entire page
    st.dataframe(
        df_scoring, 
        use_container_width=True, 
        height=min(400, 32 * len(df_scoring) + 40)
    )


# — Main UI —
if username:
    st.subheader(f"Hello, {username} 👋")
    hist_file = get_user_history_file(username)

    # 1) Ensure history file exists and has full header (backfill old rows if needed)
    if not os.path.isfile(hist_file):
        with open(hist_file, "w", newline="") as f:
            csv.writer(f).writerow(CSV_HEADER)
    else:
        # backfill missing cols
        df_existing = pd.read_csv(hist_file)
        for col in CSV_HEADER:
            if col not in df_existing.columns:
                df_existing[col] = ""
        df_existing = df_existing[CSV_HEADER]
        df_existing.to_csv(hist_file, index=False)

    # 2) Input form
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

                # — Persist into DuckDB —
        con.execute("""
          INSERT INTO sovereignty VALUES (
            ?,?,?,?,?,?,?,?,?,?,?,?,?,?
          )
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

    # 3) Show history
    st.subheader("📜 Your History")
    df_hist = con.execute(
      "SELECT timestamp, path, home_cooked_meals, junk_food, exercise_minutes, strength_training,"
     +" no_spending, invested_bitcoin, meditation, gratitude, read_or_learned, environmental_action, score"
     +" FROM sovereignty WHERE username = ? ORDER BY timestamp DESC",
      [username]
    ).df()
    if not df_hist.empty:
        st.dataframe(df_hist)
    else:
        st.info("📘 You've just created your first entry—more rows will show up here over time.")

else:
    st.warning("⚠️ Please enter your username in the sidebar to begin.")
