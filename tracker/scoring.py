# tracker/scoring.py
import json
import os

# Locate config file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, "config", "paths.json")

with open(CONFIG_FILE, "r") as f:
    ALL_PATHS = json.load(f)

def calculate_daily_score(data: dict, path: str = "default") -> int:
    if path not in ALL_PATHS:
        raise ValueError(f"Unknown scoring path: {path}")
    w = ALL_PATHS[path]
    score = 0

    # Scoring rules
    if "home_cooked_meals" in w:
        hc = w["home_cooked_meals"]
        score += min(data.get("home_cooked_meals", 0), hc["max_units"]) * hc["points_per_unit"]
    if "no_junk_food" in w and not data.get("junk_food", False):
        score += w["no_junk_food"]
    if "exercise_minutes" in w:
        em = w["exercise_minutes"]
        score += min(data.get("exercise_minutes", 0), em["max_units"]) * em["points_per_unit"]
    for k in ["strength_training", "no_spending", "invested_bitcoin", "meditation", "gratitude", "read_or_learned","environmental_action"]:
        if k in w and data.get(k, False):
            score += w[k]

    return int(round(min(score, w.get("max_score", 100))))