import json
import random
from datetime import datetime, timedelta
import duckdb
from tracker.scoring import calculate_daily_score

# Connect to DuckDB
con = duckdb.connect("data/sovereignty.duckdb")

# Load path definitions
with open("config/paths.json", "r", encoding="utf-8") as f:
    paths_config = json.load(f)

# Ensure table exists
con.execute("""
CREATE TABLE IF NOT EXISTS sovereignty (
    timestamp            TIMESTAMP,
    username             VARCHAR,
    path                 VARCHAR,
    home_cooked_meals    INTEGER,
    junk_food            BOOLEAN,
    exercise_minutes     INTEGER,
    strength_training    BOOLEAN,
    no_spending          BOOLEAN,
    invested_bitcoin     BOOLEAN,
    meditation           BOOLEAN,
    gratitude            BOOLEAN,
    read_or_learned      BOOLEAN,
    environmental_action BOOLEAN,
    score                INTEGER
);
""")

usernames = [f"user_{i}" for i in range(1, 101)]
paths = list(paths_config.keys())

for user in usernames:
    for day in range(100):
        timestamp = datetime.now() - timedelta(days=day)
        path = random.choice(paths)

        meals = random.randint(0, 3)
        junk = random.choice([True, False])
        mins = random.randint(0, 60)
        strength = random.choice([True, False])
        spending = random.choice([True, False])
        btc = random.choice([True, False])
        med = random.choice([True, False])
        grat = random.choice([True, False])
        learn = random.choice([True, False])
        env = random.choice([True, False])

        data = {
            "home_cooked_meals": meals,
            "junk_food": junk,
            "exercise_minutes": mins,
            "strength_training": strength,
            "no_spending": spending,
            "invested_bitcoin": btc,
            "meditation": med,
            "gratitude": grat,
            "read_or_learned": learn,
            "environmental_action": env
        }
        score = calculate_daily_score(data, path=path)

        con.execute("""
            INSERT INTO sovereignty VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp, user, path,
            meals, junk, mins,
            strength, spending, btc,
            med, grat, learn, env, score
        ))

print("✅ 10000 records inserted with real score logic.")
