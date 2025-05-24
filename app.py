import streamlit as st
import pandas as pd
import csv, os
import json
from datetime import datetime
from tracker.scoring import calculate_daily_score

# — Paths & setup —
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# load all path‐definitions once
PATHS_FILE = os.path.join(BASE, "config", "paths.json")
with open(PATHS_FILE, "r", encoding="utf-8") as f:
    ALL_PATHS = json.load(f)

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
}
selected_label = st.sidebar.selectbox("Scoring Profile", list(path_options.keys()))
selected_path  = path_options[selected_label]

with st.sidebar.expander("ℹ️ How this Path is Scored", expanded=False):
    st.markdown(f"**Profile:** {selected_path}")
    # flatten nested dicts into metric.submetric keys
    cfg = ALL_PATHS[selected_path]
    flat = {}
    for metric, val in cfg.items():
        if isinstance(val, dict):
            for subk, subv in val.items():
                flat[f"{metric}.{subk}"] = subv
        else:
            flat[metric] = val
    # build a 2-column DataFrame and render
    df = pd.DataFrame.from_records(
        list(flat.items()),
        columns=["metric","value"]
    )
    st.markdown("""
        <style>
        .small-font {
            font-size: 0.7em;
        }
        </style>
        <div class="small-font">
    """, unsafe_allow_html=True)
    st.table(df)
    st.markdown("</div>", unsafe_allow_html=True)

# — Main UI once username is provided —
if username:
    st.subheader(f"Hello, {username} 👋")
    hist_file = get_user_history_file(username)

    # ensure per-user CSV has header
    header = [
        "timestamp",
        "username",
        "home_cooked_meals","junk_food","exercise_minutes","strength_training",
        "no_spending","invested_bitcoin","meditation","gratitude","read_or_learned",
        "score"
    ]
    if not os.path.isfile(hist_file):
        with open(hist_file, "w", newline="") as f:
            csv.writer(f).writerow(header)

    # — Input form —
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
        submitted = st.form_submit_button("Submit & Save")

    if submitted:
        data = {
            "username": username,
            "home_cooked_meals": meals,
            "junk_food":        not junk,  # invert to match scoring logic
            "exercise_minutes": mins,
            "strength_training": lift,
            "no_spending":      spend,
            "invested_bitcoin": btc,
            "meditation":       med,
            "gratitude":        grat,
            "read_or_learned":  learn,
        }
        score = calculate_daily_score(data, path=selected_path)
        st.success(f"💪 Sovereignty Score: **{score} / 100**")
        st.info(f"Scoring Path: **{selected_label}**")

        # append to CSV
        with open(hist_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().isoformat()] + list(data.values()) + [score])

    # — Show history via pandas —
    st.subheader("📜 Your History")
    try:
        df = pd.read_csv(hist_file)
        if df.shape[0] > 0:
            st.dataframe(df)
        else:
            st.info("📘 You've just created your first entry—more rows will show up here over time.")
    except Exception:
        st.warning("⚠️ No history found yet. Submit a score to get started.")

else:
    st.warning("⚠️ Please enter your username in the sidebar to begin.")
