import streamlit as st
from datetime import datetime
from tracker.scoring import calculate_daily_score
import csv, os

# Paths
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "data")
HIST_FILE = os.path.join(DATA_DIR, "history.csv")

# Ensure history file exists
os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.isfile(HIST_FILE):
    with open(HIST_FILE, "w", newline="") as f:
        csv.writer(f).writerow(["timestamp"] + [
            "home_cooked_meals", "junk_food", "exercise_minutes",
            "strength_training", "no_spending",
            "invested_bitcoin", "meditation", "gratitude", "score"
        ])

st.title("🏰 Sovereignty Score Tracker")
st.markdown("Fill out today’s habits and hit **Submit** to see your score.")

st.sidebar.title("Choose Your Sovereignty Path")
path_options = {
    "Default (Balanced)": "default",
    "Financial Path": "financial_path",
    "Mental Resilience": "mental_resilience",
    "Physical Optimization": "physical_optimization",
    "Spiritual Growth": "spiritual_growth"
}
selected_path_label = st.sidebar.selectbox("Scoring Profile", list(path_options.keys()))
selected_path = path_options[selected_path_label]


# --- Input widgets ---
meals  = st.number_input("Home-cooked meals", min_value=0, max_value=10, value=0)
junk   = st.checkbox("No junk food today?")
mins   = st.number_input("Exercise minutes", min_value=0, max_value=300, value=0)
lift   = st.checkbox("Strength training?")
spend  = st.checkbox("No discretionary spending?")
btc    = st.checkbox("Invested in Bitcoin?")
med    = st.checkbox("Meditated?")
grat   = st.checkbox("Gratitude practice?")
learn = st.checkbox("Read a book or learned something new?")

if st.button("Submit & Save"):
    data = {
        "home_cooked_meals": meals,
        "junk_food": not junk,             # invert to match scoring logic
        "exercise_minutes": mins,
        "strength_training": lift,
        "no_spending": spend,
        "invested_bitcoin": btc,
        "meditation": med,
        "gratitude": grat,
        "read_or_learned": learn
    }
    score = calculate_daily_score(data, path=selected_path)
    st.success(f"💪 Your score: **{score} / 100**")
    st.info(f"Path used: **{selected_path_label}**")

    # Append to CSV
    with open(HIST_FILE, "a", newline="") as f:
        row = [datetime.now().isoformat()] + list(data.values()) + [score]
        csv.writer(f).writerow(row)

    # Show history
    st.subheader("📜 History")
    st.dataframe(list(csv.reader(open(HIST_FILE))), width=700)