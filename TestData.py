#!/usr/bin/env python3
"""
Generate realistic test data for Sovereignty Score system
Enhanced with performance level controls for AI coaching testing
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

class PerformanceLevel:
    EXCELLENT = "excellent"  # 80-95 average scores, high consistency
    GOOD = "good"           # 60-80 average scores, decent consistency  
    AVERAGE = "average"     # 40-65 average scores, moderate consistency
    POOR = "poor"          # 20-45 average scores, low consistency
    STRUGGLING = "struggling" # 5-25 average scores, very low consistency

def generate_realistic_user_data(username, path, days=365, performance_level=PerformanceLevel.AVERAGE):
    """Generate realistic data for a user over time with specific performance characteristics"""
    
    print(f"🎯 Generating {days} days of {performance_level.upper()} performance data")
    print(f"   User: {username} | Path: {path}")
    
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
    
    # Define user personality based on performance level and path
    personality = get_performance_personality(path, performance_level)
    
    generated_data = []
    
    for day in range(days):
        # Calculate date (going backwards from today)
        date = datetime.now() - timedelta(days=day)
        
        # Apply weekly and seasonal patterns
        day_of_week = date.weekday()  # 0=Monday, 6=Sunday
        week_of_year = date.isocalendar()[1]
        
        # Generate day's activities with performance-specific patterns
        day_data = generate_performance_activities(
            personality, day, days, day_of_week, week_of_year, btc_price, performance_level
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

def get_performance_personality(path, performance_level):
    """Define user personality traits based on path and performance level"""
    
    # Base personalities by path (from original code)
    base_personalities = {
        'default': {
            'consistency': 0.7, 'exercise_tendency': 0.6, 'cooking_tendency': 0.7,
            'btc_investment_frequency': 0.4, 'meditation_tendency': 0.5,
            'learning_tendency': 0.7, 'spending_discipline': 0.6, 'environmental_action': 0.5
        },
        'financial_path': {
            'consistency': 0.8, 'exercise_tendency': 0.5, 'cooking_tendency': 0.8,
            'btc_investment_frequency': 0.7, 'meditation_tendency': 0.4,
            'learning_tendency': 0.9, 'spending_discipline': 0.9, 'environmental_action': 0.4
        },
        'mental_resilience': {
            'consistency': 0.8, 'exercise_tendency': 0.7, 'cooking_tendency': 0.6,
            'btc_investment_frequency': 0.3, 'meditation_tendency': 0.9,
            'learning_tendency': 0.9, 'spending_discipline': 0.6, 'environmental_action': 0.5
        },
        'physical_optimization': {
            'consistency': 0.9, 'exercise_tendency': 0.95, 'cooking_tendency': 0.9,
            'btc_investment_frequency': 0.3, 'meditation_tendency': 0.6,
            'learning_tendency': 0.6, 'spending_discipline': 0.5, 'environmental_action': 0.4
        },
        'spiritual_growth': {
            'consistency': 0.7, 'exercise_tendency': 0.6, 'cooking_tendency': 0.8,
            'btc_investment_frequency': 0.2, 'meditation_tendency': 0.95,
            'learning_tendency': 0.8, 'spending_discipline': 0.7, 'environmental_action': 0.8
        },
        'planetary_stewardship': {
            'consistency': 0.8, 'exercise_tendency': 0.6, 'cooking_tendency': 0.9,
            'btc_investment_frequency': 0.3, 'meditation_tendency': 0.7,
            'learning_tendency': 0.8, 'spending_discipline': 0.8, 'environmental_action': 0.95
        }
    }
    
    # Performance level multipliers
    performance_multipliers = {
        PerformanceLevel.EXCELLENT: {
            'base_multiplier': 1.3,
            'consistency_boost': 0.95,
            'volatility': 0.05  # Very low volatility
        },
        PerformanceLevel.GOOD: {
            'base_multiplier': 1.1,
            'consistency_boost': 0.85,
            'volatility': 0.15
        },
        PerformanceLevel.AVERAGE: {
            'base_multiplier': 1.0,
            'consistency_boost': 0.70,
            'volatility': 0.25
        },
        PerformanceLevel.POOR: {
            'base_multiplier': 0.7,
            'consistency_boost': 0.45,
            'volatility': 0.40
        },
        PerformanceLevel.STRUGGLING: {
            'base_multiplier': 0.4,
            'consistency_boost': 0.25,
            'volatility': 0.60  # High volatility
        }
    }
    
    base = base_personalities.get(path, base_personalities['default'])
    multiplier_data = performance_multipliers[performance_level]
    
    # Apply performance multipliers
    personality = {}
    for trait, value in base.items():
        adjusted_value = value * multiplier_data['base_multiplier']
        # Clamp between 0.05 and 0.98
        personality[trait] = max(0.05, min(0.98, adjusted_value))
    
    # Add performance-specific traits
    personality['volatility'] = multiplier_data['volatility']
    personality['consistency_boost'] = multiplier_data['consistency_boost']
    personality['performance_level'] = performance_level
    
    return personality

def generate_performance_activities(personality, day, total_days, day_of_week, week_of_year, btc_price, performance_level):
    """Generate activities with performance-specific patterns"""
    
    # Progress factor varies by performance level
    if performance_level == PerformanceLevel.EXCELLENT:
        # Excellent performers improve quickly and maintain
        progress = min((day / (total_days * 0.3)) + 0.7, 1.0)
    elif performance_level == PerformanceLevel.GOOD:
        # Good performers have steady improvement
        progress = min((day / (total_days * 0.6)) + 0.4, 1.0)
    elif performance_level == PerformanceLevel.AVERAGE:
        # Average performers improve slowly
        progress = min(day / (total_days * 0.8), 1.0)
    elif performance_level == PerformanceLevel.POOR:
        # Poor performers start low and improve minimally
        progress = min((day / (total_days * 1.2)) + 0.1, 0.6)
    else:  # STRUGGLING
        # Struggling performers are erratic with little improvement
        progress = 0.2 + 0.3 * math.sin(day / 30)  # Cyclical struggles
    
    improvement_factor = 0.1 + (progress * 0.9)
    
    # Weekly patterns (performance level affects weekend consistency)
    is_weekend = day_of_week >= 5
    is_monday = day_of_week == 0
    
    weekend_factor = {
        PerformanceLevel.EXCELLENT: 0.95,  # Excellent performers maintain weekends
        PerformanceLevel.GOOD: 0.85,
        PerformanceLevel.AVERAGE: 0.75,
        PerformanceLevel.POOR: 0.55,
        PerformanceLevel.STRUGGLING: 0.35  # Struggling performers crash on weekends
    }[performance_level]
    
    # Seasonal patterns
    season_factor = 1.0 + 0.1 * math.sin(week_of_year * 2 * math.pi / 52)
    
    # Volatility affects random variation
    volatility = personality['volatility']
    
    def adjusted_probability(base_prob):
        prob = base_prob * improvement_factor
        if is_weekend:
            prob *= weekend_factor
        if is_monday and performance_level in [PerformanceLevel.GOOD, PerformanceLevel.EXCELLENT]:
            prob *= 1.1  # High performers get Monday boost
        prob *= season_factor
        
        # Add volatility
        volatility_adjustment = random.uniform(-volatility, volatility)
        prob += volatility_adjustment
        
        return max(0.01, min(0.99, prob))
    
    # Generate activities with performance-specific patterns
    
    # Meals - excellent performers cook more consistently
    meals_prob = adjusted_probability(personality['cooking_tendency'])
    if performance_level == PerformanceLevel.EXCELLENT:
        meals = random.choices([1, 2, 3], weights=[0.1, 0.3, 0.6])[0] if random.random() < meals_prob else 1
    elif performance_level == PerformanceLevel.STRUGGLING:
        meals = random.choices([0, 1, 2], weights=[0.6, 0.3, 0.1])[0] if random.random() < meals_prob else 0
    else:
        if random.random() < meals_prob:
            meals = random.choices([1, 2, 3], weights=[0.3, 0.5, 0.2])[0]
        else:
            meals = 0
    
    # Junk food avoidance
    junk_avoidance_prob = adjusted_probability(personality['consistency_boost'])
    junk_food = random.random() > junk_avoidance_prob
    
    # Exercise minutes - performance affects intensity and consistency
    exercise_prob = adjusted_probability(personality['exercise_tendency'])
    if random.random() < exercise_prob:
        if performance_level == PerformanceLevel.EXCELLENT:
            base_minutes = [45, 60, 75, 90, 120]
            weights = [0.2, 0.3, 0.3, 0.15, 0.05]
        elif performance_level == PerformanceLevel.STRUGGLING:
            base_minutes = [0, 10, 15, 20, 30]
            weights = [0.4, 0.3, 0.2, 0.08, 0.02]
        else:
            base_minutes = [20, 30, 45, 60, 90]
            weights = [0.2, 0.3, 0.3, 0.15, 0.05]
        
        exercise_minutes = random.choices(base_minutes, weights=weights)[0]
    else:
        exercise_minutes = 0
    
    # Strength training
    strength_prob = adjusted_probability(personality['exercise_tendency'] * 0.8)
    strength_training = random.random() < strength_prob and exercise_minutes >= 20
    
    # Spending discipline
    spending_prob = adjusted_probability(personality['spending_discipline'])
    no_spending = random.random() < spending_prob
    
    # Bitcoin investment - excellent performers invest more consistently and larger amounts
    btc_prob = adjusted_probability(personality['btc_investment_frequency'])
    if random.random() < btc_prob:
        if performance_level == PerformanceLevel.EXCELLENT:
            btc_amounts = [25, 50, 100, 200, 500]
            weights = [0.1, 0.2, 0.4, 0.2, 0.1]
        elif performance_level == PerformanceLevel.STRUGGLING:
            btc_amounts = [5, 10, 25]
            weights = [0.6, 0.3, 0.1]
        else:
            btc_amounts = [10, 25, 50, 100]
            weights = [0.3, 0.4, 0.2, 0.1]
        
        btc_usd = random.choices(btc_amounts, weights=weights)[0]
        btc_sats = usd_to_sats(btc_usd, btc_price)
        invested_bitcoin = True
    else:
        btc_usd = 0.0
        btc_sats = 0
        invested_bitcoin = False
    
    # Mental/spiritual activities
    meditation_prob = adjusted_probability(personality['meditation_tendency'])
    meditation = random.random() < meditation_prob
    
    gratitude_prob = adjusted_probability(personality['meditation_tendency'] * 0.8)
    gratitude = random.random() < gratitude_prob
    
    learning_prob = adjusted_probability(personality['learning_tendency'])
    read_or_learned = random.random() < learning_prob
    
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

def show_performance_summary(username, performance_level):
    """Show summary statistics for the generated performance data"""
    print(f"\n📊 {performance_level.upper()} PERFORMANCE SUMMARY FOR {username.upper()}")
    print("=" * 60)
    
    try:
        with get_db_connection() as conn:
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
            print(f"🧘 Meditation consistency: {meditation_days}/{total_days} ({meditation_days/total_days*100:.1f}%)")
            print(f"💪 Strength training consistency: {strength_days}/{total_days} ({strength_days/total_days*100:.1f}%)")
            print(f"🍳 Total meals cooked: {total_meals}")
            print(f"🏃 Average exercise: {avg_exercise:.1f} minutes/day")
            
            # Performance indicators
            consistency_score = (1 - (max_score - min_score) / 100) * 100
            print(f"📊 Consistency score: {consistency_score:.1f}%")
            
            # Expected coaching response
            coaching_expectations = {
                PerformanceLevel.EXCELLENT: "🎯 Should trigger CELEBRATION and OPTIMIZATION coaching",
                PerformanceLevel.GOOD: "📈 Should trigger OPTIMIZATION and encouragement coaching", 
                PerformanceLevel.AVERAGE: "⚖️ Should trigger balanced COURSE_CORRECTION coaching",
                PerformanceLevel.POOR: "🔄 Should trigger INTERVENTION and support coaching",
                PerformanceLevel.STRUGGLING: "🆘 Should trigger urgent INTERVENTION coaching"
            }
            
            print(f"\n🤖 Expected AI Coaching Response:")
            print(f"   {coaching_expectations[performance_level]}")
            
    except Exception as e:
        print(f"❌ Error generating summary: {e}")

def main():
    """Main function with interactive performance level selection"""
    print("🛡️  SOVEREIGNTY SCORE PERFORMANCE TEST DATA GENERATOR")
    print("=" * 70)
    
    # User input
    print("📝 Enter user details:")
    username = input("Username: ").strip()
    if not username:
        username = "test_user"
        print(f"Using default username: {username}")
    
    # Path selection
    paths = ['default', 'financial_path', 'mental_resilience', 'physical_optimization', 'spiritual_growth', 'planetary_stewardship']
    print(f"\n🎯 Available paths:")
    for i, path in enumerate(paths, 1):
        print(f"   {i}. {path.replace('_', ' ').title()}")
    
    try:
        path_choice = int(input(f"Select path (1-{len(paths)}): ")) - 1
        path = paths[path_choice]
    except (ValueError, IndexError):
        path = 'default'
        print(f"Using default path: {path}")
    
    # Performance level selection
    performance_levels = [
        (PerformanceLevel.EXCELLENT, "🌟 Excellent (80-95 avg, high consistency) - For testing celebration/optimization coaching"),
        (PerformanceLevel.GOOD, "👍 Good (60-80 avg, decent consistency) - For testing encouragement coaching"),
        (PerformanceLevel.AVERAGE, "⚖️ Average (40-65 avg, moderate consistency) - For testing balanced coaching"),
        (PerformanceLevel.POOR, "📉 Poor (20-45 avg, low consistency) - For testing intervention coaching"),
        (PerformanceLevel.STRUGGLING, "🆘 Struggling (5-25 avg, very low consistency) - For testing crisis coaching")
    ]
    
    print(f"\n🎭 Performance levels for AI coaching testing:")
    for i, (level, description) in enumerate(performance_levels, 1):
        print(f"   {i}. {description}")
    
    try:
        perf_choice = int(input(f"Select performance level (1-{len(performance_levels)}): ")) - 1
        performance_level = performance_levels[perf_choice][0]
    except (ValueError, IndexError):
        performance_level = PerformanceLevel.AVERAGE
        print(f"Using default performance: {performance_level}")
    
    days = 365
    print(f"\n📅 Generating {days} days of data...")
    
    # Check for existing data
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
    print(f"\n🎲 Generating {performance_level} performance data...")
    data_records = generate_realistic_user_data(username, path, days, performance_level)
    
    # Insert into database
    if insert_test_data(data_records):
        show_performance_summary(username, performance_level)
        
        print(f"\n" + "=" * 70)
        print(f"✅ SUCCESS! Generated {days} days of {performance_level} performance data")
        print(f"👤 Username: {username}")
        print(f"🎯 Path: {path}")
        print(f"🤖 Perfect for testing AI coaching responses to {performance_level} performers!")
        print("=" * 70)
    else:
        print("❌ Failed to insert test data")

if __name__ == "__main__":
    main()