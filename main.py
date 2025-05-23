import argparse
import csv
import os
import sys
from datetime import datetime


# Make sure Python can import tracker/scoring.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRACKER_DIR = os.path.join(BASE_DIR, "tracker")
sys.path.insert(0, TRACKER_DIR)

from scoring import calculate_daily_score

DATA_DIR = os.path.join(BASE_DIR, "data")
HISTORY_FILE = os.path.join(DATA_DIR, "history.csv")

# Define the questions, their keys, and how to cast the answer
FIELDS = [
    ("home_cooked_meals",  "How many home-cooked meals did you have today? (number) ", int),
    ("junk_food",         "Did you eat any junk food today? (y/n) ",               lambda x: x.lower().startswith('y')),
    ("exercise_minutes",  "How many minutes of exercise did you do? (number) ",    int),
    ("strength_training", "Did you do strength training today? (y/n) ",          lambda x: x.lower().startswith('y')),
    ("no_spending",       "Did you avoid all extraspending today? (y/n) ",             lambda x: x.lower().startswith('y')),
    ("invested_bitcoin",  "Did you invest in Bitcoin today? (y/n) ",             lambda x: x.lower().startswith('y')),
    ("meditation",        "Did you meditate today? (y/n) ",                      lambda x: x.lower().startswith('y')),
    ("gratitude",         "Did you practice gratitude today? (y/n) ",            lambda x: x.lower().startswith('y')),
    ("read_or_learned",   "Did you read a book or learn a new skill today? (y/n) ",    lambda x: x.lower().startswith('y'))
]

def list_available_paths():
    paths_file = os.path.join(BASE_DIR, "config", "paths.json")
    if not os.path.exists(paths_file):
        print("❌ paths.json not found.")
        return
    import json
    with open(paths_file, "r") as f:
        paths = json.load(f)
    print("📂 Available scoring paths:")
    for key in paths:
        print(f" - {key}")

def parse_args():
    p = argparse.ArgumentParser(description="Sovereignty Score Tracker")
    p.add_argument("--history", action="store_true", help="Show past sovereignty scores")
    p.add_argument("--clear-history", action="store_true", help="Erase all saved history")
    p.add_argument("--path", type=str, help="Scoring profile to use (e.g., 'default', 'financial_path')")
    p.add_argument("--list-paths", action="store_true", help="List available scoring paths and exit")
    return p.parse_args()



def show_history():
    """Simply dump the contents of data/history.csv to the console."""
    history_file = os.path.join(BASE_DIR, "data", "history.csv")
    if not os.path.exists(history_file):
        print("No history file found yet.")
        return
    with open(history_file, newline="") as f:
        print(f.read())

def prompt_user() -> dict:
    """Ask each question in turn, validate & cast responses."""
    answers = {}
    for key, question, caster in FIELDS:
        while True:
            resp = input(question)
            try:
                answers[key] = caster(resp)
                break
            except Exception:
                print(f"❗ Invalid input for {key!r}. Please try again.")
    return answers

def ensure_history_file():
    """Create history.csv with a header row if it doesn't yet exist."""
    if not os.path.isdir(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.isfile(HISTORY_FILE):
        with open(HISTORY_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp"] + [k for k, _, _ in FIELDS] + ["score"])

def append_to_history(data: dict, score: int):
    """Append today's responses + computed score."""
    row = [datetime.now().isoformat()] + [data[key] for key, *_ in FIELDS] + [score]
    with open(HISTORY_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)

def main(path="default"):
    print("\n=== Sovereignty Score Tracker ===\n")
    print(f"📌 Using scoring path: {path}\n")
    daily_data = prompt_user()
    score = calculate_daily_score(daily_data, path=path)
    print(f"\n💪 Your Sovereignty Score for today: {score}\n")
    ensure_history_file()
    append_to_history(daily_data, score)
    print(f"✔️  Saved to {HISTORY_FILE}\n")

if __name__ == "__main__":
    args = parse_args()

    if args.clear_history:
        if os.path.isfile(HISTORY_FILE):
            os.remove(HISTORY_FILE)
            print(f"✔️  Cleared {HISTORY_FILE}")
        else:
            print("ℹ️  No history file to clear.")
    elif args.history:
        show_history()
    elif args.list_paths:
        list_available_paths()
    else:
        selected_path = args.path if args.path else "default"
        main(path=selected_path)

