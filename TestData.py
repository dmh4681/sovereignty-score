import json
import random
from datetime import datetime, timedelta
import duckdb
from tracker.scoring import calculate_daily_score
from utils import get_current_btc_price, usd_to_sats

# Connect to DuckDB
con = duckdb.connect("data/sovereignty.duckdb")

btc_price = get_current_btc_price()
if not btc_price:
    print("⚠️ Could not fetch BTC price. Defaulting to $35,000.")
    btc_price = 100000  # fallback

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
    btc_usd              REAL DEFAULT 0,
    btc_sats             INTEGER DEFAULT 0,
    meditation           BOOLEAN,
    gratitude            BOOLEAN,
    read_or_learned      BOOLEAN,
    environmental_action BOOLEAN,
    score                INTEGER
);
""")

# Get existing users and their paths
existing_users = con.execute("""
    SELECT DISTINCT username, path 
    FROM users 
    WHERE username IN ('test', 'test2')
""").fetchall()

print("Found existing users:", existing_users)

# Generate test data
for username, path in existing_users:
    print(f"\nGenerating data for {username} on {path} path...")

    for day in range(365):
        timestamp = datetime.now() - timedelta(days=day)

        # Behavior by path
        if path == "mental_resilience":
            med = random.random() < 0.8
            grat = random.random() < 0.7
            learn = random.random() < 0.9
            mins = random.randint(20, 60)
            strength = random.random() < 0.4
        elif path == "physical_optimization":
            mins = random.randint(30, 90)
            strength = random.random() < 0.8
            med = random.random() < 0.5
            grat = random.random() < 0.5
            learn = random.random() < 0.6
        else:
            mins = random.randint(15, 45)
            strength = random.random() < 0.5
            med = random.random() < 0.6
            grat = random.random() < 0.6
            learn = random.random() < 0.7

        # Shared behaviors
        meals = random.randint(1, 3)
        junk_food = random.random() < 0.2  # True = ate junk
        no_junk_food = not junk_food       # This is what scores points
        spend = random.random() < 0.7
        btc = random.random() < 0.5
        if btc:
            btc_usd = round(random.uniform(5, 100), 2)
            btc_sats = usd_to_sats(btc_usd, btc_price)
        else:
            btc_usd, btc_sats = 0.0, 0
        env = random.random() < 0.6

        # Pass all expected fields, including `no_junk_food`
        data = {
            "home_cooked_meals": meals,
            "junk_food": junk_food,
            "no_junk_food": no_junk_food,
            "exercise_minutes": mins,
            "strength_training": strength,
            "no_spending": spend,
            "invested_bitcoin": btc,
            "btc_usd": btc_usd,
            "btc_sats": btc_sats,
            "meditation": med,
            "gratitude": grat,
            "read_or_learned": learn,
            "environmental_action": env
        }

        score = int(round(calculate_daily_score(data, path=path)))

        if day < 3:
            print(f"Day {day} | Path: {path} | Score: {score} | Data: {data}")

        # Save to DB
        con.execute("""
            INSERT INTO sovereignty VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp, username, path,
            meals, junk_food, mins,
            strength, spend, btc,
            btc_usd, btc_sats,
            med, grat, learn, env, score
        ))

print("\n✅ Test data generated for existing users.")

# Show preview
preview = con.execute("""
    SELECT username, path, COUNT(*) as entries, 
           AVG(score) as avg_score,
           MIN(timestamp) as first_entry,
           MAX(timestamp) as last_entry
    FROM sovereignty 
    GROUP BY username, path
    ORDER BY username, path
""").fetchall()

for row in preview:
    print(f"User: {row[0]}, Path: {row[1]}")
    print(f"  Entries: {row[2]}, Avg Score: {row[3]:.1f}")
    print(f"  First Entry: {row[4]}")
    print(f"  Last Entry: {row[5]}\n")
