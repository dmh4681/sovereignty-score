# -*- coding: utf-8 -*-
# tracker/scoring.py

import json
import os

# locate config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, "config", "weights.json")

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    WEIGHTS = json.load(f)

def calculate_daily_score(data: dict) -> int:
    w = WEIGHTS
    score = 0

    # 1) Home-cooked meals
    meals = data.get("home_cooked_meals", 0)
    hc_cfg = w["home_cooked_meals"]
    used_meals = min(meals, hc_cfg["max_units"])
    score += used_meals * hc_cfg["points_per_unit"]

    # 2) No junk food
    if not data.get("junk_food", False):
        score += w["no_junk_food"]

    # 3) Exercise minutes
    mins = data.get("exercise_minutes", 0)
    ex_cfg = w["exercise_minutes"]
    used_mins = min(mins, ex_cfg["max_units"])
    score += used_mins * ex_cfg["points_per_unit"]

    # 4–8) Flat booleans
    for key in ["strength_training", "no_spending", "invested_bitcoin", "meditation", "gratitude"]:
        if data.get(key, False):
            score += w[key]

    # Cap at max_score
    return int(round(min(score, w["max_score"]))) 