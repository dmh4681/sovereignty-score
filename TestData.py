import duckdb
import random
from datetime import datetime, timedelta

# Connect to your DuckDB database
con = duckdb.connect("data/sovereignty.duckdb")

usernames = [f"user_{i}" for i in range(1, 11)]
paths = ["default", "financial_path", "mental_resilience", "physical_optimization", "spiritual_growth", "planetary_stewardship"]

for user in usernames:
    for day in range(30):
        timestamp = datetime.now() - timedelta(days=day)
        path = random.choice(paths)
        meals = random.randint(0, 3)
        junk_food = random.choice([True, False])
        minutes = random.randint(0, 60)
        strength = random.choice([True, False])
        spending = random.choice([True, False])
        btc = random.choice([True, False])
        med = random.choice([True, False])
        grat = random.choice([True, False])
        learn = random.choice([True, False])
        env = random.choice([True, False])
        score = random.randint(50, 100)

        con.execute("""
            INSERT INTO sovereignty VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp, user, path,
            meals, junk_food, minutes,
            strength, spending, btc,
            med, grat, learn, env, score
        ))

print("✅ 300 sample records inserted.")
