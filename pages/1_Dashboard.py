import streamlit as st

st.set_page_config(
    page_title="Sovereignty Dashboard",
    page_icon="📊",
    layout="wide"
)

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from db import get_db_connection

# Get user info from query params or session state
username = st.query_params.get("username", None) or st.session_state.get("username", None)
path = st.query_params.get("path", None) or st.session_state.get("path", None)

# Store in session state if we got it from query params
if st.query_params.get("username"):
    st.session_state.username = st.query_params.get("username")
if st.query_params.get("path"):
    st.session_state.path = st.query_params.get("path")

if not username or not path:
    st.error("Please log in through the main page to access your dashboard.")
    st.stop()

st.title("📊 Your Sovereignty Dashboard")

# Load user's data
try:
    with get_db_connection() as conn:
        df = conn.execute("""
            SELECT timestamp, score, 
                home_cooked_meals, junk_food, exercise_minutes, 
                strength_training, no_spending, invested_bitcoin,
                meditation, gratitude, read_or_learned, 
                environmental_action
            FROM sovereignty 
            WHERE username = ?
            ORDER BY timestamp DESC
        """, [username]).df()
        
    if df.empty:
        st.info("📘 No data yet. Start tracking your habits to see your dashboard!")
        st.stop()
        
    # Convert timestamp to datetime if it's not already
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Focus on last 30 days
    last_30_days = df[df['timestamp'] >= datetime.now() - timedelta(days=30)]

    # Average score over 30 days
    avg_30_score = last_30_days['score'].mean()
    std_30_score = last_30_days['score'].std()

    # Score stability: high std = volatile, low = consistent
    score_consistency = "High" if std_30_score < 10 else "Moderate" if std_30_score < 20 else "Low"

    # High-level metrics row
    m1, m2 = st.columns(2)
    with m1:
        st.metric("📊 30-Day Avg Score", f"{avg_30_score:.1f}/100")
    with m2:
        st.metric("📉 Score Consistency", score_consistency)
    
    # Create two columns for metrics
    col1, col2 = st.columns(2)
    
    with col1:
        # Overall score trend
        st.subheader("🎯 Score Trend")
        fig = px.line(df, x='timestamp', y='score',
                     title='Your Daily Sovereignty Score',
                     labels={'score': 'Score', 'timestamp': 'Date'})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent scores
        st.subheader("📈 Recent Scores")
        recent_scores = df.head(7)[['timestamp', 'score']]
        recent_scores['timestamp'] = recent_scores['timestamp'].dt.strftime('%Y-%m-%d')
        st.dataframe(recent_scores, hide_index=True)
        
    with col2:
        # Habit completion rates
        st.subheader("✅ Habit Completion")
        habits = ['home_cooked_meals', 'junk_food', 'exercise_minutes', 
                 'strength_training', 'no_spending', 'invested_bitcoin',
                 'meditation', 'gratitude', 'read_or_learned', 
                 'environmental_action']
        
        completion_rates = []
        for habit in habits:
            if habit == 'home_cooked_meals':
                # For meals, calculate average
                rate = df[habit].mean()
                label = f"Avg {habit.replace('_', ' ').title()}"
            elif habit == 'exercise_minutes':
                # For exercise, calculate average minutes
                rate = df[habit].mean()
                label = f"Avg {habit.replace('_', ' ').title()}"
            else:
                # For boolean habits, calculate completion rate
                rate = df[habit].mean() * 100
                label = f"{habit.replace('_', ' ').title()} Rate"
            
            completion_rates.append({
                'Habit': label,
                'Rate': rate
            })
            
        completion_df = pd.DataFrame(completion_rates)
        fig = px.bar(completion_df, x='Habit', y='Rate',
                    title='Habit Completion Rates',
                    labels={'Rate': 'Completion Rate (%)'})
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
    # Add more visualizations here as needed

    # 🔻 Most Missed Habits (Boolean only)
    st.subheader("🚩 Most Missed Habits")
    bool_habits = [
        'junk_food', 'strength_training', 'no_spending',
        'invested_bitcoin', 'meditation', 'gratitude',
        'read_or_learned', 'environmental_action'
    ]

    habit_miss_rates = []
    for habit in bool_habits:
        # Flip junk_food logic since True = bad
        if habit == "junk_food":
            miss_rate = df[habit].mean() * 100  # % of days junk was consumed
            label = "Ate Junk Food"
        else:
            miss_rate = 100 - df[habit].mean() * 100
            label = habit.replace('_', ' ').title()
        
        habit_miss_rates.append((label, miss_rate))

    miss_df = pd.DataFrame(habit_miss_rates, columns=["Habit", "Miss Rate (%)"])
    miss_df = miss_df.sort_values(by="Miss Rate (%)", ascending=False).head(5)

    st.dataframe(miss_df, use_container_width=True, hide_index=True)

    # ₿ Bitcoin Stacking Summary
    st.subheader("🟠 Bitcoin Activity")

    btc_days = df[df['invested_bitcoin'] == True]
    total_btc_usd = btc_days['btc_usd'].sum()
    total_btc_sats = btc_days['btc_sats'].sum()
    avg_usd = btc_days['btc_usd'].mean()
    avg_sats = btc_days['btc_sats'].mean()

    col_btc1, col_btc2 = st.columns(2)
    with col_btc1:
        st.metric("💵 Total USD Invested", f"${total_btc_usd:,.2f}")
        st.metric("📅 Stacking Days", f"{len(btc_days)} days")
    with col_btc2:
        st.metric("⚡ Total Sats Stacked", f"{int(total_btc_sats):,}")
        st.metric("📈 Avg Sats/Day", f"{int(avg_sats or 0):,}")


    
except Exception as e:
    st.error(f"Error loading dashboard data: {str(e)}") 