#!/usr/bin/env python3
"""
Data Intelligence Agent - Sovereignty Score Behavioral Analytics
Analyzes user patterns and generates insights for AI coaching system
"""

import os
import sys
import json
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection

class DataIntelligenceAgent:
    """
    Analyzes user behavioral patterns and generates structured insights
    for the AI coaching system
    """
    
    def __init__(self):
        self.insights = {}
        
    def analyze_user(self, username, analysis_days=90):
        """
        Comprehensive analysis of user behavior patterns
        
        Args:
            username (str): User to analyze
            analysis_days (int): Number of recent days to analyze deeply
            
        Returns:
            dict: Structured behavioral insights
        """
        print(f"🔍 Analyzing behavioral patterns for {username}...")
        
        try:
            with get_db_connection() as conn:
                # Get user's path and basic info
                user_info = self._get_user_info(conn, username)
                if not user_info:
                    return None
                
                # Get all user data for comprehensive analysis
                all_data = self._get_user_data(conn, username)
                recent_data = self._get_recent_data(conn, username, analysis_days)
                
                if not all_data:
                    return {"error": "No data found for user"}
                
                # Perform comprehensive analysis
                insights = {
                    "user_profile": user_info,
                    "data_summary": self._analyze_data_summary(all_data),
                    "streak_analysis": self._analyze_streaks(all_data),
                    "trend_analysis": self._analyze_trends(all_data, recent_data),
                    "consistency_patterns": self._analyze_consistency(all_data),
                    "path_performance": self._analyze_path_performance(all_data, user_info["path"]),
                    "behavioral_insights": self._generate_behavioral_insights(all_data, recent_data),
                    "coaching_opportunities": self._identify_coaching_opportunities(all_data, recent_data),
                    "timestamp": datetime.now().isoformat()
                }
                
                self.insights[username] = insights
                return insights
                
        except Exception as e:
            print(f"❌ Error analyzing user {username}: {e}")
            return {"error": str(e)}
    
    def _get_user_info(self, conn, username):
        """Get basic user information"""
        try:
            user = conn.execute("""
                SELECT username, path, created_at FROM users WHERE username = ?
            """, [username]).fetchone()
            
            if user:
                return {
                    "username": user[0],
                    "path": user[1],
                    "created_at": user[2].isoformat() if user[2] else None
                }
            return None
        except:
            # Fallback if users table doesn't exist or user not found
            data_check = conn.execute("""
                SELECT DISTINCT username, path FROM sovereignty WHERE username = ? LIMIT 1
            """, [username]).fetchone()
            
            if data_check:
                return {
                    "username": data_check[0],
                    "path": data_check[1],
                    "created_at": None
                }
            return None
    
    def _get_user_data(self, conn, username):
        """Get all user sovereignty data"""
        return conn.execute("""
            SELECT timestamp, score, home_cooked_meals, junk_food, exercise_minutes,
                   strength_training, no_spending, invested_bitcoin, btc_usd, btc_sats,
                   meditation, gratitude, read_or_learned, environmental_action
            FROM sovereignty 
            WHERE username = ? 
            ORDER BY timestamp DESC
        """, [username]).fetchall()
    
    def _get_recent_data(self, conn, username, days):
        """Get recent user data"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return conn.execute("""
            SELECT timestamp, score, home_cooked_meals, junk_food, exercise_minutes,
                   strength_training, no_spending, invested_bitcoin, btc_usd, btc_sats,
                   meditation, gratitude, read_or_learned, environmental_action
            FROM sovereignty 
            WHERE username = ? AND timestamp >= ?
            ORDER BY timestamp DESC
        """, [username, cutoff_date]).fetchall()
    
    def _analyze_data_summary(self, data):
        """Generate basic data summary statistics"""
        if not data:
            return {}
        
        scores = [row[1] for row in data if row[1] is not None]
        btc_investments = [row[8] for row in data if row[8] and row[8] > 0]
        exercise_sessions = [row[4] for row in data if row[4] and row[4] > 0]
        
        return {
            "total_days": len(data),
            "date_range": {
                "start": data[-1][0].isoformat() if data else None,
                "end": data[0][0].isoformat() if data else None
            },
            "score_stats": {
                "average": round(statistics.mean(scores), 1) if scores else 0,
                "median": round(statistics.median(scores), 1) if scores else 0,
                "min": min(scores) if scores else 0,
                "max": max(scores) if scores else 0,
                "std_dev": round(statistics.stdev(scores), 1) if len(scores) > 1 else 0
            },
            "activity_totals": {
                "total_btc_invested": round(sum(btc_investments), 2),
                "total_sats": sum(row[9] for row in data if row[9]),
                "total_meals_cooked": sum(row[2] for row in data if row[2]),
                "total_exercise_minutes": sum(row[4] for row in data if row[4]),
                "meditation_days": sum(1 for row in data if row[10]),
                "learning_days": sum(1 for row in data if row[12])
            }
        }
    
    def _analyze_streaks(self, data):
        """Analyze current and historical streaks for all activities"""
        if not data:
            return {}
        
        # Define activities to track streaks for
        activities = {
            "meditation": 10,
            "gratitude": 11,
            "read_or_learned": 12,
            "environmental_action": 13,
            "strength_training": 5,
            "no_spending": 6,
            "invested_bitcoin": 7
        }
        
        streak_analysis = {}
        
        for activity, col_index in activities.items():
            current_streak = 0
            longest_streak = 0
            temp_streak = 0
            total_days = 0
            
            # Sort data chronologically for streak calculation
            sorted_data = sorted(data, key=lambda x: x[0])
            
            for row in sorted_data:
                if row[col_index]:  # Activity was done
                    temp_streak += 1
                    longest_streak = max(longest_streak, temp_streak)
                    total_days += 1
                else:
                    temp_streak = 0
            
            # Current streak is the temp_streak if it continues to today
            current_streak = temp_streak
            
            streak_analysis[activity] = {
                "current_streak": current_streak,
                "longest_streak": longest_streak,
                "total_days": total_days,
                "consistency_rate": round(total_days / len(data) * 100, 1) if data else 0
            }
        
        return streak_analysis
    
    def _analyze_trends(self, all_data, recent_data):
        """Analyze trends comparing recent performance to historical"""
        if not all_data or not recent_data:
            return {}
        
        # Calculate averages for different time periods
        all_scores = [row[1] for row in all_data if row[1] is not None]
        recent_scores = [row[1] for row in recent_data if row[1] is not None]
        
        # Get first 30 days for comparison
        early_data = sorted(all_data, key=lambda x: x[0])[:30]
        early_scores = [row[1] for row in early_data if row[1] is not None]
        
        trend_analysis = {
            "score_trends": {
                "all_time_average": round(statistics.mean(all_scores), 1) if all_scores else 0,
                "recent_average": round(statistics.mean(recent_scores), 1) if recent_scores else 0,
                "early_average": round(statistics.mean(early_scores), 1) if early_scores else 0,
                "improvement": round(statistics.mean(recent_scores) - statistics.mean(early_scores), 1) if recent_scores and early_scores else 0,
                "trend_direction": "improving" if recent_scores and early_scores and statistics.mean(recent_scores) > statistics.mean(early_scores) else "declining" if recent_scores and early_scores else "stable"
            }
        }
        
        # Analyze activity trends
        activities = ["meditation", "strength_training", "invested_bitcoin", "read_or_learned"]
        activity_indices = [10, 5, 7, 12]
        
        for activity, idx in zip(activities, activity_indices):
            all_rate = sum(1 for row in all_data if row[idx]) / len(all_data) * 100
            recent_rate = sum(1 for row in recent_data if row[idx]) / len(recent_data) * 100 if recent_data else 0
            
            trend_analysis[f"{activity}_trend"] = {
                "all_time_rate": round(all_rate, 1),
                "recent_rate": round(recent_rate, 1),
                "change": round(recent_rate - all_rate, 1)
            }
        
        return trend_analysis
    
    def _analyze_consistency(self, data):
        """Analyze consistency patterns (weekday vs weekend, etc.)"""
        if not data:
            return {}
        
        weekday_scores = []
        weekend_scores = []
        
        for row in data:
            day_of_week = row[0].weekday()  # 0=Monday, 6=Sunday
            score = row[1]
            
            if score is not None:
                if day_of_week < 5:  # Monday-Friday
                    weekday_scores.append(score)
                else:  # Saturday-Sunday
                    weekend_scores.append(score)
        
        return {
            "weekday_performance": {
                "average_score": round(statistics.mean(weekday_scores), 1) if weekday_scores else 0,
                "consistency": round(100 - statistics.stdev(weekday_scores), 1) if len(weekday_scores) > 1 else 0
            },
            "weekend_performance": {
                "average_score": round(statistics.mean(weekend_scores), 1) if weekend_scores else 0,
                "consistency": round(100 - statistics.stdev(weekend_scores), 1) if len(weekend_scores) > 1 else 0
            },
            "weekend_drop": round(statistics.mean(weekday_scores) - statistics.mean(weekend_scores), 1) if weekday_scores and weekend_scores else 0
        }
    
    def _analyze_path_performance(self, data, path):
        """Analyze how well user is performing on their chosen path"""
        if not data:
            return {}
        
        # Load path configuration
        try:
            config_path = os.path.join(os.path.dirname(__file__), "config", "paths.json")
            with open(config_path, 'r') as f:
                paths_config = json.load(f)
            
            path_config = paths_config.get(path, {})
            max_score = path_config.get("max_score", 100)
            
        except:
            max_score = 100
        
        scores = [row[1] for row in data if row[1] is not None]
        avg_score = statistics.mean(scores) if scores else 0
        
        # Calculate path-specific metrics
        path_performance = {
            "path_alignment_score": round(avg_score / max_score * 100, 1),
            "path_mastery_level": self._get_mastery_level(avg_score, max_score),
            "optimal_score_achievement": round(len([s for s in scores if s >= max_score * 0.8]) / len(scores) * 100, 1) if scores else 0
        }
        
        # Add path-specific analysis
        if path == "financial_path":
            btc_investments = [row[8] for row in data if row[8] and row[8] > 0]
            path_performance["financial_metrics"] = {
                "investment_frequency": round(len(btc_investments) / len(data) * 100, 1),
                "average_investment": round(statistics.mean(btc_investments), 2) if btc_investments else 0
            }
        elif path == "physical_optimization":
            exercise_days = [row for row in data if row[4] and row[4] > 0]
            path_performance["physical_metrics"] = {
                "exercise_frequency": round(len(exercise_days) / len(data) * 100, 1),
                "strength_training_rate": round(sum(1 for row in data if row[5]) / len(data) * 100, 1)
            }
        
        return path_performance
    
    def _get_mastery_level(self, avg_score, max_score):
        """Determine mastery level based on average score"""
        percentage = avg_score / max_score * 100
        
        if percentage >= 80:
            return "Master"
        elif percentage >= 65:
            return "Advanced"
        elif percentage >= 50:
            return "Intermediate"
        elif percentage >= 35:
            return "Developing"
        else:
            return "Beginner"
    
    def _generate_behavioral_insights(self, all_data, recent_data):
        """Generate high-level behavioral insights"""
        if not all_data:
            return {}
        
        # Analyze engagement patterns
        days_since_last_entry = (datetime.now() - all_data[0][0]).days
        
        # Analyze score volatility
        scores = [row[1] for row in all_data if row[1] is not None]
        score_volatility = statistics.stdev(scores) if len(scores) > 1 else 0
        
        insights = {
            "engagement_level": "high" if days_since_last_entry <= 1 else "moderate" if days_since_last_entry <= 3 else "low",
            "days_since_last_entry": days_since_last_entry,
            "behavioral_stability": "stable" if score_volatility < 15 else "variable" if score_volatility < 25 else "volatile",
            "score_volatility": round(score_volatility, 1),
            "motivation_indicators": self._assess_motivation_indicators(all_data, recent_data)
        }
        
        return insights
    
    def _assess_motivation_indicators(self, all_data, recent_data):
        """Assess current motivation level based on recent patterns"""
        if not recent_data:
            return {"level": "unknown", "indicators": []}
        
        recent_scores = [row[1] for row in recent_data if row[1] is not None]
        
        # Check for positive indicators
        positive_indicators = []
        negative_indicators = []
        
        if recent_scores:
            if statistics.mean(recent_scores) > 50:
                positive_indicators.append("Good recent performance")
            if len(recent_scores) >= 7:
                positive_indicators.append("Consistent logging")
            if max(recent_scores) >= 80:
                positive_indicators.append("Recent high scores achieved")
        
        # Check for concerning patterns
        if len(recent_scores) < 5:
            negative_indicators.append("Inconsistent logging")
        if recent_scores and statistics.mean(recent_scores) < 30:
            negative_indicators.append("Low recent scores")
        
        # Determine overall motivation level
        if len(positive_indicators) > len(negative_indicators):
            level = "high"
        elif len(negative_indicators) > len(positive_indicators):
            level = "low"
        else:
            level = "moderate"
        
        return {
            "level": level,
            "positive_indicators": positive_indicators,
            "negative_indicators": negative_indicators
        }
    
    def _identify_coaching_opportunities(self, all_data, recent_data):
        """Identify specific coaching opportunities"""
        opportunities = []
        
        if not all_data:
            return opportunities
        
        # Check for celebration opportunities
        streak_data = self._analyze_streaks(all_data)
        for activity, stats in streak_data.items():
            if stats["current_streak"] >= 7:
                opportunities.append({
                    "type": "celebration",
                    "focus": activity,
                    "message": f"Celebrate {stats['current_streak']}-day {activity} streak"
                })
        
        # Check for intervention opportunities
        if recent_data:
            recent_scores = [row[1] for row in recent_data if row[1] is not None]
            if recent_scores and statistics.mean(recent_scores) < 40:
                opportunities.append({
                    "type": "intervention",
                    "focus": "overall_performance",
                    "message": "Recent scores suggest need for support and course correction"
                })
        
        # Check for optimization opportunities
        all_scores = [row[1] for row in all_data if row[1] is not None]
        if all_scores and statistics.mean(all_scores) > 60:
            opportunities.append({
                "type": "optimization",
                "focus": "performance_enhancement",
                "message": "Strong foundation - ready for advanced sovereignty practices"
            })
        
        return opportunities

def main():
    """Test the Data Intelligence Agent with our test users"""
    print("🤖 SOVEREIGNTY DATA INTELLIGENCE AGENT")
    print("=" * 60)
    
    agent = DataIntelligenceAgent()
    
    # Test with all our test users
    test_users = ["test3", "test_planetary", "test_physical", "test_financial"]
    
    for username in test_users:
        print(f"\n🔍 Analyzing {username}...")
        insights = agent.analyze_user(username)
        
        if insights and "error" not in insights:
            print(f"✅ Analysis complete for {username}")
            
            # Show key insights
            data_summary = insights.get("data_summary", {})
            behavioral = insights.get("behavioral_insights", {})
            path_perf = insights.get("path_performance", {})
            
            print(f"   📊 {data_summary.get('total_days', 0)} days tracked")
            print(f"   🏆 Average score: {data_summary.get('score_stats', {}).get('average', 0)}")
            print(f"   🎯 Path mastery: {path_perf.get('path_mastery_level', 'Unknown')}")
            print(f"   🔥 Motivation: {behavioral.get('motivation_indicators', {}).get('level', 'Unknown')}")
            
            # Show coaching opportunities
            opportunities = insights.get("coaching_opportunities", [])
            if opportunities:
                print(f"   💡 Coaching opportunities: {len(opportunities)}")
                for opp in opportunities[:2]:  # Show first 2
                    print(f"      • {opp['type'].title()}: {opp['message']}")
        else:
            print(f"❌ Error analyzing {username}: {insights.get('error', 'Unknown error')}")
    
    print(f"\n" + "=" * 60)
    print("🚀 Data Intelligence Agent testing complete!")
    print("Ready to build the next agent in the coaching pipeline...")
    print("=" * 60)

if __name__ == "__main__":
    main()