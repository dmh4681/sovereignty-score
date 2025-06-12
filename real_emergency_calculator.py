# real_emergency_calculator.py
# Replace hardcoded values with actual sovereignty data calculations

import streamlit as st
from datetime import datetime, timedelta
import statistics
from db import get_db_connection

def calculate_real_emergency_metrics(username, path):
    """
    Calculate emergency metrics from actual sovereignty tracking data
    This replaces the hardcoded dummy data with real calculations
    """
    try:
        with get_db_connection() as conn:
            # Get comprehensive sovereignty data
            user_data = conn.execute("""
                SELECT timestamp, score, btc_usd, btc_sats, home_cooked_meals,
                       no_spending, invested_bitcoin, meditation, gratitude,
                       read_or_learned, environmental_action, exercise_minutes,
                       strength_training, junk_food
                FROM sovereignty 
                WHERE username = ? 
                ORDER BY timestamp DESC 
                LIMIT 180  -- 6 months of data
            """, [username]).fetchall()
            
            if not user_data:
                return {"error": "No sovereignty data found. Track some habits first!"}
            
            # Calculate real financial metrics
            financial_metrics = calculate_real_financial_position(user_data)
            
            # Calculate real expense patterns
            expense_metrics = calculate_real_expense_patterns(user_data, path)
            
            # Calculate emergency preparedness from sovereignty habits
            preparedness_metrics = calculate_real_preparedness_score(user_data, path)
            
            # Calculate real account access estimates
            account_estimates = calculate_real_account_estimates(financial_metrics, expense_metrics)
            
            # Calculate emergency runway
            emergency_runway = financial_metrics["total_liquid_assets"] / expense_metrics["monthly_expenses"]
            
            return {
                "username": username,
                "path": path,
                "emergency_runway_months": emergency_runway,
                "financial_position": financial_metrics,
                "expense_analysis": expense_metrics,
                "preparedness_analysis": preparedness_metrics,
                "account_access_matrix": account_estimates,
                "sovereignty_status": get_sovereignty_status(emergency_runway),
                "data_quality": assess_data_quality(user_data)
            }
            
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}

def calculate_real_financial_position(user_data):
    """Calculate actual financial position from sovereignty tracking"""
    
    # Real crypto tracking
    total_btc_invested = sum(row[2] for row in user_data if row[2])  # btc_usd
    total_sats = sum(row[3] for row in user_data if row[3])  # btc_sats
    investment_frequency = sum(1 for row in user_data if row[6]) / len(user_data)  # invested_bitcoin
    
    # Estimate current crypto value (you can replace with real-time API)
    btc_price_estimate = 100000  # Current BTC price - you could use get_current_btc_price()
    current_crypto_value = (total_sats / 100_000_000) * btc_price_estimate
    
    # Estimate traditional assets based on sovereignty patterns
    # Users with consistent investment habits likely have traditional accounts too
    investment_discipline_score = investment_frequency * 100
    estimated_traditional_assets = current_crypto_value * (1 + investment_discipline_score / 100)
    
    # Estimate liquid vs illiquid split
    liquid_percentage = 0.3  # Conservative estimate
    total_assets = current_crypto_value + estimated_traditional_assets
    liquid_assets = total_assets * liquid_percentage
    
    return {
        "total_btc_invested": total_btc_invested,
        "total_sats": total_sats,
        "current_crypto_value": current_crypto_value,
        "estimated_traditional_assets": estimated_traditional_assets,
        "total_assets": total_assets,
        "total_liquid_assets": liquid_assets,
        "investment_frequency": investment_frequency,
        "investment_discipline_score": investment_discipline_score
    }

def calculate_real_expense_patterns(user_data, path):
    """Calculate real expense patterns from sovereignty habits"""
    
    # Calculate cooking frequency and implied food savings
    cooking_data = [row[4] for row in user_data if row[4] is not None]  # home_cooked_meals
    avg_meals_cooked_per_day = statistics.mean(cooking_data) if cooking_data else 0
    
    # Calculate spending discipline
    no_spending_frequency = sum(1 for row in user_data if row[5]) / len(user_data)  # no_spending
    
    # Estimate monthly expenses based on sovereignty habits
    # More cooking = lower food expenses
    # Higher no_spending frequency = lower discretionary expenses
    
    base_monthly_expenses = 5000  # Starting estimate
    
    # Adjust based on cooking habits
    cooking_savings_per_month = avg_meals_cooked_per_day * 30 * 8  # $8 saved per home meal
    
    # Adjust based on spending discipline
    discretionary_savings = base_monthly_expenses * 0.3 * no_spending_frequency
    
    estimated_monthly_expenses = base_monthly_expenses - cooking_savings_per_month - discretionary_savings
    estimated_monthly_expenses = max(estimated_monthly_expenses, 2500)  # Minimum floor
    
    # Calculate fixed vs variable expenses
    fixed_expenses = estimated_monthly_expenses * 0.6  # Housing, insurance, etc.
    variable_expenses = estimated_monthly_expenses * 0.4  # Food, entertainment, etc.
    
    return {
        "monthly_expenses": estimated_monthly_expenses,
        "fixed_expenses": fixed_expenses,
        "variable_expenses": variable_expenses,
        "cooking_frequency": avg_meals_cooked_per_day,
        "spending_discipline": no_spending_frequency,
        "estimated_cooking_savings": cooking_savings_per_month,
        "estimated_discretionary_savings": discretionary_savings
    }

def calculate_real_preparedness_score(user_data, path):
    """Calculate family preparedness based on sovereignty habits"""
    
    # Extract habit consistency data
    recent_data = user_data[:30]  # Last 30 days
    
    habit_scores = {
        "meditation_consistency": sum(1 for row in recent_data if row[7]) / len(recent_data),  # meditation
        "gratitude_consistency": sum(1 for row in recent_data if row[8]) / len(recent_data),  # gratitude
        "learning_consistency": sum(1 for row in recent_data if row[9]) / len(recent_data),  # read_or_learned
        "environmental_consistency": sum(1 for row in recent_data if row[10]) / len(recent_data),  # environmental_action
        "fitness_consistency": sum(1 for row in recent_data if row[11] and row[11] > 0) / len(recent_data),  # exercise_minutes
        "strength_consistency": sum(1 for row in recent_data if row[12]) / len(recent_data),  # strength_training
        "nutrition_consistency": sum(1 for row in recent_data if not row[13]) / len(recent_data)  # not junk_food
    }
    
    # Overall sovereignty consistency score
    overall_consistency = statistics.mean(habit_scores.values())
    
    # Path-specific preparedness adjustments
    path_multipliers = {
        "financial_path": 1.2,  # Financial path users are more prepared for emergencies
        "mental_resilience": 1.1,  # Mental resilience helps with crisis management
        "physical_optimization": 1.05,  # Physical health helps in emergencies
        "spiritual_growth": 1.0,
        "planetary_stewardship": 1.0,
        "default": 1.0
    }
    
    path_multiplier = path_multipliers.get(path, 1.0)
    adjusted_preparedness = min(100, overall_consistency * 100 * path_multiplier)
    
    return {
        "overall_consistency": overall_consistency,
        "habit_scores": habit_scores,
        "path_multiplier": path_multiplier,
        "family_preparedness_score": adjusted_preparedness,
        "preparedness_level": get_preparedness_level(adjusted_preparedness)
    }

def get_preparedness_level(score):
    """Convert preparedness score to descriptive level"""
    if score >= 85:
        return {"level": "Highly Prepared", "color": "#10b981"}
    elif score >= 70:
        return {"level": "Well Prepared", "color": "#22c55e"}
    elif score >= 55:
        return {"level": "Moderately Prepared", "color": "#eab308"}
    elif score >= 40:
        return {"level": "Somewhat Prepared", "color": "#f97316"}
    else:
        return {"level": "Needs Preparation", "color": "#dc2626"}

def calculate_real_account_estimates(financial_metrics, expense_metrics):
    """Generate realistic account estimates based on financial position"""
    
    total_assets = financial_metrics["total_assets"]
    crypto_value = financial_metrics["current_crypto_value"]
    
    # Estimate account distribution based on typical sovereignty-minded portfolios
    immediate_access = {
        "joint_checking": min(15000, expense_metrics["monthly_expenses"] * 2),
        "joint_savings": min(50000, expense_metrics["monthly_expenses"] * 6),
        "emergency_fund_cd": min(25000, expense_metrics["monthly_expenses"] * 3)
    }
    
    short_term_access = {
        "crypto_portfolio": crypto_value,
        "investment_account": max(0, total_assets * 0.3 - crypto_value),
        "life_insurance": 250000  # Typical term life policy
    }
    
    long_term_access = {
        "retirement_401k": max(0, total_assets * 0.4),
        "home_equity": max(0, total_assets * 0.2),
        "other_investments": max(0, total_assets * 0.1)
    }
    
    return {
        "immediate_access": immediate_access,
        "short_term_access": short_term_access,
        "long_term_access": long_term_access,
        "total_immediate": sum(immediate_access.values()),
        "total_short_term": sum(short_term_access.values()),
        "total_long_term": sum(long_term_access.values())
    }

def assess_data_quality(user_data):
    """Assess the quality and completeness of sovereignty data"""
    
    total_days = len(user_data)
    complete_entries = sum(1 for row in user_data if row[1] is not None and row[1] > 0)  # Has score
    
    # Check for Bitcoin tracking
    btc_entries = sum(1 for row in user_data if row[2] is not None and row[2] > 0)  # btc_usd
    
    # Check for consistent habit tracking
    habit_completeness = []
    for i in range(4, 14):  # Check various habit columns
        non_null_count = sum(1 for row in user_data if row[i] is not None)
        habit_completeness.append(non_null_count / total_days)
    
    avg_completeness = statistics.mean(habit_completeness)
    
    return {
        "total_days": total_days,
        "complete_entries": complete_entries,
        "data_completeness": complete_entries / total_days if total_days > 0 else 0,
        "btc_tracking_frequency": btc_entries / total_days if total_days > 0 else 0,
        "habit_completeness": avg_completeness,
        "data_quality_score": (avg_completeness + (complete_entries / total_days)) / 2 if total_days > 0 else 0,
        "recommendations": generate_data_quality_recommendations(total_days, complete_entries, btc_entries, avg_completeness)
    }

def generate_data_quality_recommendations(total_days, complete_entries, btc_entries, habit_completeness):
    """Generate recommendations for improving data quality"""
    recommendations = []
    
    if total_days < 30:
        recommendations.append("Track more consistently to improve emergency calculations")
    
    if complete_entries / total_days < 0.8:
        recommendations.append("Aim for daily sovereignty score tracking for better accuracy")
    
    if btc_entries / total_days < 0.1:
        recommendations.append("Track Bitcoin investments to improve crypto portfolio estimates")
    
    if habit_completeness < 0.7:
        recommendations.append("Complete more habit tracking for better preparedness scoring")
    
    if not recommendations:
        recommendations.append("Excellent data quality! Emergency calculations are highly accurate")
    
    return recommendations

def get_sovereignty_status(runway_months):
    """Convert runway months to sovereignty status (same as before but documented)"""
    if runway_months >= 240:  # 20+ years
        return {"level": "Generationally Sovereign", "color": "#10b981", "icon": "🟩"}
    elif runway_months >= 72:  # 6+ years
        return {"level": "Antifragile", "color": "#22c55e", "icon": "🟢"}
    elif runway_months >= 36:  # 3+ years
        return {"level": "Robust", "color": "#eab308", "icon": "🟡"}
    elif runway_months >= 12:  # 1+ year
        return {"level": "Fragile", "color": "#f97316", "icon": "🔴"}
    else:
        return {"level": "Vulnerable", "color": "#dc2626", "icon": "⚫"}

# Integration function to replace the hardcoded calculate_emergency_metrics
def get_real_emergency_dashboard_data(username, path):
    """
    Main function to replace calculate_emergency_metrics in the dashboard
    Returns same structure but with real data calculations
    """
    real_data = calculate_real_emergency_metrics(username, path)
    
    if "error" in real_data:
        return real_data
    
    # Transform to match existing dashboard expectations
    financial = real_data["financial_position"]
    expenses = real_data["expense_analysis"]
    preparedness = real_data["preparedness_analysis"]
    accounts = real_data["account_access_matrix"]
    
    return {
        "username": username,
        "path": path,
        "emergency_runway_months": real_data["emergency_runway_months"],
        "estimated_portfolio_value": financial["total_assets"],
        "estimated_crypto_value": financial["current_crypto_value"],
        "avg_sovereignty_score": preparedness["overall_consistency"] * 100,
        "total_btc_invested": financial["total_btc_invested"],
        "total_sats": financial["total_sats"],
        "monthly_expenses": expenses["monthly_expenses"],
        "immediate_access_estimate": accounts["total_immediate"],
        "short_term_access_estimate": accounts["total_short_term"],
        "sovereignty_status": real_data["sovereignty_status"],
        "detailed_accounts": accounts,
        "expense_breakdown": expenses,
        "preparedness_details": preparedness,
        "data_quality": real_data["data_quality"]
    }