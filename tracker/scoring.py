# tracker/scoring.py
import json
import os

# Load the scoring config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, "config", "paths.json")

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    ALL_PATHS = json.load(f)

def calculate_daily_score(data: dict, path: str = "default") -> int:
    if path not in ALL_PATHS:
        raise ValueError(f"Unknown scoring path: {path}")

    config = ALL_PATHS[path]
    score = 0

    # Home-cooked meals
    if "home_cooked_meals" in config:
        hc_cfg = config["home_cooked_meals"]
        units = min(data.get("home_cooked_meals", 0), hc_cfg.get("max_units", 0))
        score += units * hc_cfg.get("points_per_unit", 0)

    # Junk food logic: only add points if NO junk food
    if "no_junk_food" in config and not data.get("junk_food", False):
        score += config["no_junk_food"]

    # Exercise minutes
    if "exercise_minutes" in config:
        ex_cfg = config["exercise_minutes"]
        minutes = min(data.get("exercise_minutes", 0), ex_cfg.get("max_units", 0))
        score += minutes * ex_cfg.get("points_per_unit", 0)

    # Booleans
    for key in [
        "strength_training", "no_spending", "invested_bitcoin",
        "meditation", "gratitude", "read_or_learned", "environmental_action"
    ]:
        if key in config and data.get(key, False):
            score += config[key]

    # Final cap and rounding
    return min(round(score), config.get("max_score", 100))
