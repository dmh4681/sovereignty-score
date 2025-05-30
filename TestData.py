#!/usr/bin/env python3
"""
Generate realistic test data for Sovereignty Score system
Updated for new database structure and field order fixes
"""

import json
import random
import math
from datetime import datetime, timedelta
import duckdb
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tracker.scoring import calculate_daily_score
from utils import get_current_btc_price, usd_to_sats
from db import get_db_connection

def generate_realistic_user_data(username, path, days=365):
    """Generate realistic data for a user over time with trends and patterns"""
    
    print(f"🎯 Generating {days} days of data for {username} on {path} path...")
    
    # Get BTC price (with fallback)
    btc_price = get_current_btc_price()
    if not btc_price:
        print("⚠️ Could not fetch BTC price. Using $95,000 as fallback.")
        btc_price = 95000
    else:
        print(f"💰 Using current BTC price: ${btc_price:,.0f}")
    
    # Load path configuration for this user
    config_path = os.path.join(os.path.dirname(__file__), "config", "paths.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        paths_config = json.load(f)
    
    if path not in paths_config:
        raise ValueError(f"Unknown path: {path}")
    
    # Define user personality and trends based on path
    personality = get_user_personality(path)
    
    generated_data = []
    
    for day in range(days):
        # Calculate date (going backwards from today)
        date = datetime.now() - timedelta(days=day)
        
        # Apply weekly and seasonal patterns
        day_of_week = date.weekday()  # 0=Monday, 6=Sunday
        week_of_year = date.isocalendar()[1]
        
        # Generate day's activities with realistic patterns
        day_data = generate_daily_activities(
            personality, day, days, day_of_week, week_of_year, btc_price
        )
        
        # Calculate score using the actual scoring system
        try:
            score = calculate_daily_score(day_data, path=path)
            score = max(0, min(100, int(round(score))))
        except Exception as e:
            print(f"⚠️ Error calculating score for day {day}: {e}")
            score = 50  # Fallback score
        
        # Prepare database record
        record = {
            'timestamp': date,
            'username': username,
            'path': path,
            'home_cooked_meals': day_data['home_cooked_meals'],
            'junk_food': day_data['junk_food'],
            'exercise_minutes': day_data['exercise_minutes'],
            'strength_training': day_data['strength_training'],
            'no_spending': day_data['no_spending'],
            'invested_bitcoin': day_data['invested_bitcoin'],
            'btc_usd': day_data['btc_usd'],
            'btc_sats': day_data['btc_sats'],
            'meditation': day_data['meditation'],
            'gratitude': day_data['gratitude'],
            'read_or_learned': day_data['read_or_learned'],
            'environmental_action': day_data['environmental_action'],
            'score': score
        }
        
        generated_data.append(record)
        
        # Show progress and sample data for first few days
        if day < 5:
            print(f"   Day {day+1}: Score {score}, Meals {day_data['home_cooked_meals']}, "
                  f"Exercise {day_data['exercise_minutes']}min, BTC ${day_data['btc_usd']:.2f}")
    
    return generated_data

def get_user_personality(path):
    """Define user personality traits based on their chosen path"""
    personalities = {
        'default': {
            'consistency': 0.7,
            'exercise_tendency': 0.6,
            'cooking_tendency': 0.7,
            'btc_investment_frequency': 0.4,
            'meditation_tendency': 0.5,
            'learning_tendency': 0.7,
            'spending_discipline': 0.6,
            'environmental_action': 0.5
        },
        'financial_path': {
            'consistency': 0.8,
            'exercise_tendency': 0.5,
            'cooking_tendency': 0.8,  # High - saves money
            'btc_investment_frequency': 0.7,  # Very high
            'meditation_tendency': 0.4,
            'learning_tendency': 0.9,  # Very high - always learning
            'spending_discipline': 0.9,  # Extremely disciplined
            'environmental_action': 0.4
        },
        'mental_resilience': {
            'consistency': 0.8,
            'exercise_tendency': 0.7,
            'cooking_tendency': 0.6,
            'btc_investment_frequency': 0.3,
            'meditation_tendency': 0.9,  # Very high
            'learning_tendency': 0.9,  # Very high
            'spending_discipline': 0.6,
            'environmental_action': 0.5
        },
        'physical_optimization': {
            'consistency': 0.9,  # Very consistent
            'exercise_tendency': 0.95,  # Almost daily
            'cooking_tendency': 0.9,  # High - nutrition focused
            'btc_investment_frequency': 0.3,
            'meditation_tendency': 0.6,
            'learning_tendency': 0.6,
            'spending_discipline': 0.5,
            'environmental_action': 0.4
        },
        'spiritual_growth': {
            'consistency': 0.7,
            'exercise_tendency': 0.6,
            'cooking_tendency': 0.8,  # Mindful eating
            'btc_investment_frequency': 0.2,
            'meditation_tendency': 0.95,  # Almost daily
            'learning_tendency': 0.8,
            'spending_discipline': 0.7,
            'environmental_action': 0.8  # High environmental consciousness
        },
        'planetary_stewardship': {
            'consistency': 0.8,
            'exercise_tendency': 0.6,
            'cooking_tendency': 0.9,  # Sustainable eating
            'btc_investment_frequency': 0.3,
            'meditation_tendency': 0.7,
            'learning_tendency': 0.8,
            'spending_discipline': 0.8,  # Conscious consumption
            'environmental_action': 0.95  # Almost daily
        }
    }
    
    return personalities.get(path, personalities['default'])

def generate_daily_activities(personality, day, total_days, day_of_week, week_of_year, btc_price):
    """Generate realistic daily activities based on personality and patterns"""
    
    # Progress factor (user gets better over time)
    progress = min(day / (total_days * 0.8), 1.0)  # Plateau at 80% through the year
    improvement_factor = 0.3 + (progress * 0.7)  # Scale from 30% to 100% consistency
    
    # Weekly patterns
    is_weekend = day_of_week >= 5
    is_monday = day_of_week == 0  # "New week, new me" effect
    
    # Seasonal patterns (holidays, New Year's resolutions, summer activity)
    season_factor = 1.0 + 0.2 * math.sin(week_of_year * 2 * math.pi / 52)
    
    # Apply personality with improvement and patterns
    def adjusted_probability(base_prob):
        prob = base_prob * improvement_factor
        if is_weekend:
            prob *= 0.9  # Slightly lower consistency on weekends
        if is_monday:
            prob *= 1.1  # Monday motivation boost
        prob *= season_factor
        return min(max(prob, 0.05), 0.95)  # Keep between 5% and 95%
    
    # Generate activities
    
    # Home cooked meals (1-3 per day, weighted by personality)
    meals_prob = adjusted_probability(personality['cooking_tendency'])
    if random.random() < meals_prob:
        meals = random.choices([1, 2, 3], weights=[0.3, 0.5, 0.2])[0]
    else:
        meals = random.choices([0, 1], weights=[0.7, 0.3])[0]
    
    # Junk food (True = ate junk food, False = avoided)
    junk_avoidance_prob = adjusted_probability(personality['consistency'])
    junk_food = random.random() > junk_avoidance_prob
    
    # Exercise minutes
    exercise_prob = adjusted_probability(personality['exercise_tendency'])
    if random.random() < exercise_prob:
        base_minutes = [20, 30, 45, 60, 90]
        weights = [0.2, 0.3, 0.3, 0.15, 0.05]
        exercise_minutes = random.choices(base_minutes, weights=weights)[0]
        if is_weekend:
            exercise_minutes = int(exercise_minutes * 1.2)  # Longer weekend workouts
    else:
        exercise_minutes = random.choices([0, 10, 15], weights=[0.7, 0.2, 0.1])[0]
    
    # Strength training
    strength_prob = adjusted_probability(personality['exercise_tendency'] * 0.7)  # Slightly less frequent
    strength_training = random.random() < strength_prob and exercise_minutes >= 20
    
    # No discretionary spending
    spending_prob = adjusted_probability(personality['spending_discipline'])
    no_spending = random.random() < spending_prob
    
    # Bitcoin investment
    btc_prob = adjusted_probability(personality['btc_investment_frequency'])
    if random.random() < btc_prob:
        # More realistic investment amounts based on user type
        if personality['btc_investment_frequency'] > 0.6:  # Financial path users
            btc_amounts = [10, 25, 50, 100, 200]
            weights = [0.1, 0.3, 0.3, 0.2, 0.1]
        else:
            btc_amounts = [5, 10, 25, 50]
            weights = [0.3, 0.4, 0.2, 0.1]
        
        btc_usd = random.choices(btc_amounts, weights=weights)[0]
        btc_sats = usd_to_sats(btc_usd, btc_price)
        invested_bitcoin = True
    else:
        btc_usd = 0.0
        btc_sats = 0
        invested_bitcoin = False
    
    # Meditation
    meditation_prob = adjusted_probability(personality['meditation_tendency'])
    meditation = random.random() < meditation_prob
    
    # Gratitude
    gratitude_prob = adjusted_probability(personality['meditation_tendency'] * 0.8)  # Correlates with meditation
    gratitude = random.random() < gratitude_prob
    
    # Learning
    learning_prob = adjusted_probability(personality['learning_tendency'])
    read_or_learned = random.random() < learning_prob
    
    # Environmental action
    env_prob = adjusted_probability(personality['environmental_action'])
    environmental_action = random.random() < env_prob
    
    return {
        'home_cooked_meals': meals,
        'junk_food': junk_food,
        'exercise_minutes': exercise_minutes,
        'strength_training': strength_training,
        'no_spending': no_spending,
        'invested_bitcoin': invested_bitcoin,
        'btc_usd': float(btc_usd),
        'btc_sats': int(btc_sats),
        'meditation': meditation,
        'gratitude': gratitude,
        'read_or_learned': read_or_learned,
        'environmental_action': environmental_action
    }

def insert_test_data(data_records):
    """Insert test data into database using proper field order"""
    print(f"💾 Inserting {len(data_records)} records into database...")
    
    try:
        with get_db_connection() as conn:
            # Use explicit column names to avoid field order issues
            for record in data_records:
                conn.execute("""
                    INSERT INTO sovereignty (
                        timestamp, username, path,
                        home_cooked_meals, junk_food, exercise_minutes, strength_training,
                        no_spending, invested_bitcoin, btc_usd, btc_sats,
                        meditation, gratitude, read_or_learned, environmental_action, score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    record['timestamp'], record['username'], record['path'],
                    record['home_cooked_meals'], record['junk_food'], record['exercise_minutes'], 
                    record['strength_training'], record['no_spending'], record['invested_bitcoin'], 
                    record['btc_usd'], record['btc_sats'], record['meditation'], record['gratitude'], 
                    record['read_or_learned'], record['environmental_action'], record['score']
                ])
        
        print("✅ All records inserted successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error inserting data: {e}")
        return False

def show_summary_stats(username):
    """Show summary statistics for the generated data"""
    print(f"\n📊 SUMMARY STATISTICS FOR {username.upper()}")
    print("=" * 50)
    
    try:
        with get_db_connection() as conn:
            # Get basic stats
            stats = conn.execute("""
                SELECT 
                    COUNT(*) as total_days,
                    AVG(score) as avg_score,
                    MIN(score) as min_score,
                    MAX(score) as max_score,
                    SUM(btc_usd) as total_btc_invested,
                    SUM(btc_sats) as total_sats,
                    SUM(CASE WHEN meditation THEN 1 ELSE 0 END) as meditation_days,
                    SUM(CASE WHEN strength_training THEN 1 ELSE 0 END) as strength_days,
                    SUM(home_cooked_meals) as total_meals,
                    AVG(exercise_minutes) as avg_exercise
                FROM sovereignty 
                WHERE username = ?
            """, [username]).fetchone()
            
            total_days, avg_score, min_score, max_score, total_btc, total_sats, \
            meditation_days, strength_days, total_meals, avg_exercise = stats
            
            print(f"📅 Total days tracked: {total_days}")
            print(f"🏆 Average score: {avg_score:.1f}/100")
            print(f"📈 Score range: {min_score} - {max_score}")
            print(f"💰 Total Bitcoin invested: ${total_btc:,.2f}")
            print(f"⚡ Total sats accumulated: {total_sats:,}")
            print(f"🧘 Meditation days: {meditation_days}/{total_days} ({meditation_days/total_days*100:.1f}%)")
            print(f"💪 Strength training days: {strength_days}/{total_days} ({strength_days/total_days*100:.1f}%)")
            print(f"🍳 Total home-cooked meals: {total_meals}")
            print(f"🏃 Average exercise: {avg_exercise:.1f} minutes/day")
            
            # Get recent vs early performance
            recent_avg = conn.execute("""
                SELECT AVG(score) FROM sovereignty 
                WHERE username = ? 
                ORDER BY timestamp DESC LIMIT 30
            """, [username]).fetchone()[0]
            
            early_avg = conn.execute("""
                SELECT AVG(score) FROM sovereignty 
                WHERE username = ? 
                ORDER BY timestamp ASC LIMIT 30
            """, [username]).fetchone()[0]
            
            improvement = recent_avg - early_avg
            print(f"📈 Improvement: {improvement:+.1f} points (recent 30 days vs first 30 days)")
            
    except Exception as e:
        print(f"❌ Error generating summary: {e}")

def main():
    """Main function to generate test data"""
    print("🛡️  SOVEREIGNTY SCORE TEST DATA GENERATOR")
    print("=" * 60)
    
    # Configuration
    username = "test3"
    path = "default"  # You can change this
    days = 365
    
    print(f"👤 Generating data for user: {username}")
    print(f"🎯 Path: {path}")
    print(f"📅 Days: {days}")
    
    # Check if user already has data
    try:
        with get_db_connection() as conn:
            existing_count = conn.execute(
                "SELECT COUNT(*) FROM sovereignty WHERE username = ?", [username]
            ).fetchone()[0]
            
            if existing_count > 0:
                print(f"⚠️  User {username} already has {existing_count} records")
                response = input("Delete existing data and regenerate? (y/N): ").strip().lower()
                if response == 'y':
                    conn.execute("DELETE FROM sovereignty WHERE username = ?", [username])
                    print(f"🗑️  Deleted {existing_count} existing records")
                else:
                    print("❌ Cancelled - keeping existing data")
                    return
    except Exception as e:
        print(f"❌ Error checking existing data: {e}")
        return
    
    # Generate data
    print(f"\n🎲 Generating realistic data...")
    data_records = generate_realistic_user_data(username, path, days)
    
    # Insert into database
    if insert_test_data(data_records):
        show_summary_stats(username)
        
        print(f"\n" + "=" * 60)
        print(f"✅ SUCCESS! Generated {days} days of test data for {username}")
        print(f"🚀 You can now log in as {username} to see the full history")
        print(f"💡 Try different paths by changing the 'path' variable in this script")
        print("=" * 60)
    else:
        print("❌ Failed to insert test data")

if __name__ == "__main__":
    main()