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

# Get existing users and their paths
existing_users = con.execute("""
    SELECT DISTINCT username, path 
    FROM users 
    WHERE username IN ('test', 'test2')
""").fetchall()

print("Found existing users:", existing_users)

# Generate test data for each existing user
for username, path in existing_users:
    print(f"\nGenerating data for {username} on {path} path...")
    
    # Generate 30 days of data
    for day in range(30):
        timestamp = datetime.now() - timedelta(days=day)
        
        # Generate realistic data based on path
        if path == "mental_resilience":
            # Higher probability of meditation, learning, and gratitude
            med = random.random() < 0.8
            grat = random.random() < 0.7
            learn = random.random() < 0.9
            # Moderate exercise
            mins = random.randint(20, 60)
            strength = random.random() < 0.4
        elif path == "physical_optimization":
            # Higher probability of exercise and strength training
            mins = random.randint(30, 90)
            strength = random.random() < 0.8
            med = random.random() < 0.5
            grat = random.random() < 0.5
            learn = random.random() < 0.6
        else:
            # Default balanced approach
            mins = random.randint(15, 45)
            strength = random.random() < 0.5
            med = random.random() < 0.6
            grat = random.random() < 0.6
            learn = random.random() < 0.7

        # Common metrics with some randomness
        meals = random.randint(1, 3)
        junk = random.random() < 0.2  # 20% chance of junk food
        spending = random.random() < 0.7  # 70% chance of no spending
        btc = random.random() < 0.3  # 30% chance of Bitcoin investment
        env = random.random() < 0.6  # 60% chance of environmental action

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
            timestamp, username, path,
            meals, junk, mins,
            strength, spending, btc,
            med, grat, learn, env, score
        ))

print("\n✅ Test data generated for existing users.")

# Preview the data
print("\nData Preview:")
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
