import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from db import get_db_connection

# Get user info from query params
username = st.query_params.get("username", None)
path = st.query_params.get("path", None)

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
    
except Exception as e:
    st.error(f"Error loading dashboard data: {str(e)}") 