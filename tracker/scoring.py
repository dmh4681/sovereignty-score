import json
import os

# Load all path configurations
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, "config", "paths.json")

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    ALL_PATHS = json.load(f)

def calculate_daily_score(data: dict, path: str = "default") -> int:
    if path not in ALL_PATHS:
        raise ValueError(f"Unknown scoring path: {path}")
    
    config = ALL_PATHS[path]
    score = 0

    # Meal-based score
    if "home_cooked_meals" in config:
        meal_cfg = config["home_cooked_meals"]
        meals = data.get("home_cooked_meals", 0)
        capped_meals = min(meals, meal_cfg.get("max_units", 1))
        score += capped_meals * meal_cfg.get("points_per_unit", 0)

    # Junk food avoidance
    if "no_junk_food" in config:
        if not data.get("junk_food", False):
            score += config["no_junk_food"]

    # Exercise minutes
    if "exercise_minutes" in config:
        ex_cfg = config["exercise_minutes"]
        mins = data.get("exercise_minutes", 0)
        capped_mins = min(mins, ex_cfg.get("max_units", 1))
        score += capped_mins * ex_cfg.get("points_per_unit", 0)

    # Binary habits
    binary_keys = [
        "strength_training",
        "no_spending",
        "invested_bitcoin",
        "meditation",
        "gratitude",
        "read_or_learned",
        "environmental_action"
    ]

    for key in binary_keys:
        if key in config and data.get(key, False):
            score += config[key]

    # Optional max score cap (default to 100)
    return int(round(min(score, config.get("max_score", 100))))
