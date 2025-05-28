# tracker/scoring.py
import json
import os

# Locate and load the config file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, "config", "paths.json")

with open(CONFIG_FILE, "r") as f:
    ALL_PATHS = json.load(f)

def calculate_daily_score(data: dict, path: str = "default") -> int:
    if path not in ALL_PATHS:
        raise ValueError(f"Unknown scoring path: {path}")

    config = ALL_PATHS[path]
    score = 0

    # Home-cooked meals (points per unit up to max)
    if "home_cooked_meals" in config:
        meal_cfg = config["home_cooked_meals"]
        meals = data.get("home_cooked_meals", 0)
        score += min(meals, meal_cfg["max_units"]) * meal_cfg["points_per_unit"]

    # No junk food (only if junk_food is False)
    if "no_junk_food" in config:
        if not data.get("junk_food", False):  # User did NOT eat junk
            score += config["no_junk_food"]

    # Exercise minutes
    if "exercise_minutes" in config:
        ex_cfg = config["exercise_minutes"]
        minutes = data.get("exercise_minutes", 0)
        score += min(minutes, ex_cfg["max_units"]) * ex_cfg["points_per_unit"]

    # One-off booleans (strength, gratitude, etc.)
    single_keys = [
        "strength_training", "no_spending", "invested_bitcoin",
        "meditation", "gratitude", "read_or_learned", "environmental_action"
    ]
    for key in single_keys:
        if key in config and data.get(key, False):
            score += config[key]

    # Clamp to max_score (typically 100)
    return int(round(min(score, config.get("max_score", 100))))
