import streamlit as st
from datetime import datetime
from tracker.scoring import calculate_daily_score
import csv, os

# Paths
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Title and UI
st.title("🏰 Sovereignty Score Tracker")
st.markdown("Track your sovereign choices. Enter your habits, get a score, and visualize your progress.")

# Sidebar for username and scoring path
st.sidebar.title("User & Path")
username = st.sidebar.text_input("Enter your username:", max_chars=30)

path_options = {
    "Default (Balanced)": "default",
    "Financial Path": "financial_path",
    "Mental Resilience": "mental_resilience",
    "Physical Optimization": "physical_optimization",
    "Spiritual Growth": "spiritual_growth"
}
selected_path_label = st.sidebar.selectbox("Scoring Profile", list(path_options.keys()))
selected_path = path_options[selected_path_label]

# Determine user's history file
def get_user_history_file(username: str) -> str:
    safe_user = username.strip().lower().replace(" ", "_")
    return os.path.join(DATA_DIR, f"history_{safe_user}.csv")

# Input form
if username:
    st.subheader(f"Hello, {username} 👋")

    with st.form("tracker_form"):
        meals  = st.number_input("Home-cooked meals", min_value=0, max_value=10, value=0)
        junk   = st.checkbox("No junk food today?")
        mins   = st.number_input("Exercise minutes", min_value=0, max_value=300, value=0)
        lift   = st.checkbox("Strength training?")
        spend  = st.checkbox("No discretionary spending?")
        btc    = st.checkbox("Invested in Bitcoin?")
        med    = st.checkbox("Meditated?")
        grat   = st.checkbox("Gratitude practice?")
        learn  = st.checkbox("Read or learned something new?")
        submitted = st.form_submit_button("Submit & Save")

    if submitted:
        data = {
            "home_cooked_meals": meals,
            "junk_food": not junk,
            "exercise_minutes": mins,
            "strength_training": lift,
            "no_spending": spend,
            "invested_bitcoin": btc,
            "meditation": med,
            "gratitude": grat,
            "read_or_learned": learn
        }
        score = calculate_daily_score(data, path=selected_path)
        st.success(f"💪 Sovereignty Score: **{score} / 100**")
        st.info(f"Scoring Path: **{selected_path_label}**")

        # Save to per-user history
        hist_file = get_user_history_file(username)
        file_exists = os.path.isfile(hist_file)

        with open(hist_file, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp"] + list(data.keys()) + ["score"])
            writer.writerow([datetime.now().isoformat()] + list(data.values()) + [score])

        # Show history
    st.subheader("📜 Your History")
    with open(hist_file, newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
        if len(rows) > 1:
            st.dataframe(rows[1:], columns=rows[0])
        elif len(rows) == 1:
            st.info("📘 You’ve just submitted your first entry. More rows will appear here over time.")
        else:
            st.warning("⚠️ No history found yet.")

else:
    st.warning("⚠️ Please enter your username in the sidebar to begin.")
