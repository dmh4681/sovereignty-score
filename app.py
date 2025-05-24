import streamlit as st
import pandas as pd
import csv, os, json
from datetime import datetime
from tracker.scoring import calculate_daily_score

# — Paths & setup —
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Load all scoring paths
PATHS_FILE = os.path.join(BASE, "config", "paths.json")
with open(PATHS_FILE, "r", encoding="utf-8") as f:
    ALL_PATHS = json.load(f)

# Default CSV header
CSV_HEADER = [
    "timestamp", "username", "home_cooked_meals", "junk_food", "exercise_minutes",
    "strength_training", "no_spending", "invested_bitcoin", "meditation",
    "gratitude", "read_or_learned", "environmental_action", "score"
]

def get_user_history_file(username: str) -> str:
    safe = username.strip().lower().replace(" ", "_")
    return os.path.join(DATA_DIR, f"history_{safe}.csv")

# — Page title & sidebar —
st.title("🏰 Sovereignty Score Tracker")
st.markdown("Track your sovereign choices. Enter your habits, get a score, and visualize your progress.")

st.sidebar.title("User & Path")
username = st.sidebar.text_input("Enter your username:", max_chars=30)

path_options = {
    "Default (Balanced)":       "default",
    "Financial Path":           "financial_path",
    "Mental Resilience":        "mental_resilience",
    "Physical Optimization":    "physical_optimization",
    "Spiritual Growth":         "spiritual_growth",
    "Planetary Stewardship":    "planetary_stewardship",
}

# Preselect path from URL if present
# Preselect path from URL if present (Streamlit 1.32+)
query_params = st.query_params
default_path = query_params.get("path", [None])[0] if query_params else None
selected_label = st.sidebar.selectbox(
    "Scoring Profile",
    list(path_options.keys()),
    index=list(path_options.values()).index(default_path) if default_path in path_options.values() else 0
)
selected_path = path_options[selected_label]

# Sidebar breakdown
with st.sidebar.expander("ℹ️ How this Path is Scored", expanded=False):
    st.markdown(f"**Profile:** {selected_path}")
    cfg = ALL_PATHS[selected_path]
    flat = {}
    for metric, val in cfg.items():
        if isinstance(val, dict):
            for subk, subv in val.items():
                flat[f"{metric}.{subk}"] = subv
        else:
            flat[metric] = val
    df = pd.DataFrame.from_records(list(flat.items()), columns=["metric", "value"])
    st.markdown("<style>.small-font { font-size: 0.7em; }</style><div class='small-font'>", unsafe_allow_html=True)
    st.table(df)
    st.markdown("</div>", unsafe_allow_html=True)

# — Main UI —
if username:
    st.subheader(f"Hello, {username} 👋")
    hist_file = get_user_history_file(username)

    # Ensure history file exists and matches current schema
    if not os.path.isfile(hist_file):
        with open(hist_file, "w", newline="") as f:
            csv.writer(f).writerow(CSV_HEADER)
    else:
        # Backfill any missing columns in history file
        with open(hist_file, "r", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
        if rows:
            header = rows[0]
            missing = [col for col in CSV_HEADER if col not in header]
            if missing:
                # Pad existing rows and rewrite with fixed header
                updated = [CSV_HEADER]
                for row in rows[1:]:
                    padded = row + [""] * (len(CSV_HEADER) - len(row))
                    updated.append(padded)
                with open(hist_file, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerows(updated)

    # Form UI
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
            "username": username,
            "home_cooked_meals": meals,
            "junk_food":        not junk,
            "exercise_minutes": mins,
            "strength_training": lift,
            "no_spending":      spend,
            "invested_bitcoin": btc,
            "meditation":       med,
            "gratitude":        grat,
            "read_or_learned":  learn,
            "environmental_action": env,
        }
        score = calculate_daily_score(data, path=selected_path)
        st.success(f"💪 Sovereignty Score: **{score} / 100**")
        st.info(f"Scoring Path: **{selected_label}**")

        # Save to history
        with open(hist_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().isoformat()] + list(data.values()) + [score])

    # Show history
    st.subheader("📜 Your History")
    try:
        df = pd.read_csv(hist_file)
        if not df.empty:
            st.dataframe(df)
        else:
            st.info("📘 You've just created your first entry—more rows will show up here over time.")
    except Exception:
        st.warning("⚠️ No history found yet. Submit a score to get started.")
else:
    st.warning("⚠️ Please enter your username in the sidebar to begin.")
