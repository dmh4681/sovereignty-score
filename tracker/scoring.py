# tracker/scoring.py
import json
import os

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, "config", "weights.json")

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    WEIGHTS = json.load(f)

def calculate_daily_score(data: dict) -> int:
    w = WEIGHTS
    score = 0

    # 1) Home-cooked meals
    hc_cfg = w["home_cooked_meals"]
    meals = min(data.get("home_cooked_meals", 0), hc_cfg["max_units"])
    score += meals * hc_cfg["points_per_unit"]

    # 2) No junk food
    if not data.get("junk_food", False):
        score += w["no_junk_food"]

    # 3) Exercise minutes
    ex_cfg = w["exercise_minutes"]
    mins = min(data.get("exercise_minutes", 0), ex_cfg["max_units"])
    score += mins * ex_cfg["points_per_unit"]

    # 4–8) flat booleans
    if data.get("strength_training", False):
        score += w["strength_training"]
    if data.get("no_spending", False):
        score += w["no_spending"]
    if data.get("invested_bitcoin", False):
        score += w["invested_bitcoin"]
    if data.get("meditation", False):
        score += w["meditation"]
    if data.get("gratitude", False):
        score += w["gratitude"]

    # cap at configured max
    return int(round(min(score, w["max_score"])))