# updated_page_6_family_finance.py
"""
Updated Page 6 - Family Finance Plan
Integrates database storage with existing emergency dashboard
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from family_finance_database import FamilyFinanceDB
from family_finance_forms import (
    render_financial_setup_wizard,
    render_quick_update_form
)
from improved_emergency_features import (
    render_enhanced_emergency_status,
    render_enhanced_crypto_recovery,
    render_enhanced_family_planning
)

# Get user context
username = st.query_params.get("username", None) or st.session_state.get("username", None)
path = st.query_params.get("path", None) or st.session_state.get("path", None)

if not username or not path:
    st.error("❌ Please log in through the main dashboard first")
    st.stop()

# Initialize database
finance_db = FamilyFinanceDB()

def check_user_setup_status(username: str) -> bool:
    """Check if user has completed financial setup"""
    accounts = finance_db.get_accounts_by_priority(username)
    expenses = finance_db.get_expense_summary(username)
    
    # User needs setup if they have no accounts or expenses
    has_accounts = any(accounts[priority] for priority in accounts)
    has_expenses = len(expenses['expenses']) > 0
    
    return has_accounts and has_expenses

def get_current_btc_price() -> float:
    """Get current BTC price - integrate with your existing price fetcher"""
    try:
        conn = get_db_connection()
        result = conn.execute("""
            SELECT closing_price 
            FROM btc_price_history 
            ORDER BY date DESC 
            LIMIT 1
        """).fetchone()
        return result[0] if result else 50000.0  # Default fallback
    except:
        return 50000.0

def calculate_enhanced_emergency_metrics(username: str, path: str):
    """Calculate emergency metrics using real database data"""
    
    btc_price = get_current_btc_price()
    
    # Get sovereignty metrics from database
    metrics = finance_db.calculate_sovereignty_metrics(username, btc_price)
    
    # Get account breakdown
    accounts = finance_db.get_accounts_by_priority(username)
    
    # Calculate access totals
    access_totals = {
        'immediate': sum(acc['balance'] for acc in accounts.get('immediate', [])),
        'short_term': sum(acc['balance'] for acc in accounts.get('short_term', [])),
        'medium_term': sum(acc['balance'] for acc in accounts.get('medium_term', [])),
        'long_term': sum(acc['balance'] for acc in accounts.get('long_term', []))
    }
    
    # Get crypto details
    crypto_summary = finance_db.get_crypto_summary(username)
    btc_amount = crypto_summary.get('BTC', {}).get('total_amount', 0)
    
    # Build emergency data structure matching existing dashboard expectations
    emergency_data = {
        "username": username,
        "path": path,
        "emergency_runway_months": metrics['emergency_runway_months'],
        "estimated_portfolio_value": metrics['total_assets'],
        "estimated_crypto_value": metrics['total_crypto_value'],
        "total_btc": btc_amount,
        "total_sats": int(btc_amount * 100_000_000),
        "monthly_expenses": metrics['monthly_expenses'],
        "immediate_access_estimate": access_totals['immediate'],
        "short_term_access_estimate": access_totals['short_term'],
        "sovereignty_status": metrics['sovereignty_status'],
        "sovereignty_ratio": metrics['sovereignty_ratio'],
        "full_sovereignty_ratio": metrics['full_sovereignty_ratio'],
        "btc_price": btc_price,
        "detailed_accounts": accounts,
        "expense_breakdown": finance_db.get_expense_summary(username)
    }
    
    # Save snapshot for tracking
    finance_db.save_sovereignty_snapshot(username, metrics)
    
    return emergency_data

def render_enhanced_account_matrix(data: dict, username: str):
    """Enhanced account access matrix using real data"""
    
    st.markdown("## 💰 Account Access Priority Matrix")
    
    accounts = data['detailed_accounts']
    
    # Immediate Access
    st.markdown("### 🟢 IMMEDIATE ACCESS (0-24 hours)")
    if accounts['immediate']:
        df_immediate = pd.DataFrame([
            {
                "Account": acc['account_name'],
                "Type": acc['account_type'],
                "Balance": f"${acc['balance']:,.0f}",
                "Access": acc['access_method'] or "See notes",
                "Joint": "✅" if acc['is_joint'] else "❌"
            }
            for acc in accounts['immediate']
        ])
        st.dataframe(df_immediate, hide_index=True, use_container_width=True)
    else:
        st.warning("No immediate access accounts configured")
    
    # Short-term Access
    st.markdown("### 🟡 SHORT-TERM ACCESS (1-14 days)")
    if accounts['short_term']:
        df_short = pd.DataFrame([
            {
                "Account": acc['account_name'],
                "Type": acc['account_type'],
                "Balance": f"${acc['balance']:,.0f}",
                "Access": acc['access_method'] or "See notes",
                "Days": acc['days_to_access']
            }
            for acc in accounts['short_term']
        ])
        st.dataframe(df_short, hide_index=True, use_container_width=True)
    else:
        st.info("No short-term accounts configured")
    
    # Long-term Access
    st.markdown("### 🔴 LONG-TERM ACCESS (2+ weeks)")
    if accounts['long_term']:
        df_long = pd.DataFrame([
            {
                "Account": acc['account_name'],
                "Type": acc['account_type'],
                "Balance": f"${acc['balance']:,.0f}",
                "Access": acc['access_method'] or "See notes",
                "Timeline": f"{acc['days_to_access']}+ days"
            }
            for acc in accounts['long_term']
        ])
        st.dataframe(df_long, hide_index=True, use_container_width=True)
    else:
        st.info("No long-term accounts configured")
    
    # Summary metrics
    st.markdown("### 📊 Access Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Immediate Funds", 
                  f"${data['immediate_access_estimate']:,.0f}",
                  f"{data['immediate_access_estimate']/data['monthly_expenses']:.1f} months")
    
    with col2:
        total_liquid = data['immediate_access_estimate'] + data['short_term_access_estimate']
        st.metric("Liquid Funds (< 2 weeks)", 
                  f"${total_liquid:,.0f}",
                  f"{total_liquid/data['monthly_expenses']:.1f} months")
    
    with col3:
        st.metric("Total Portfolio", 
                  f"${data['estimated_portfolio_value']:,.0f}",
                  data['sovereignty_status'])
    
    with col4:
        st.metric("Sovereignty Ratio",
                  f"{data['sovereignty_ratio']:.2f}",
                  "Years of freedom")

def render_sovereignty_dashboard(data: dict):
    """Enhanced sovereignty status overview"""
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #059669, #10b981); 
                padding: 20px; 
                border-radius: 10px; 
                margin-bottom: 20px;">
        <h2 style="color: white; margin: 0; text-align: center;">
            Your Sovereignty Status: {status}
        </h2>
        <p style="color: #d1fae5; margin: 10px 0 0 0; text-align: center; font-size: 20px;">
            {ratio:.1f} years of financial sovereignty | ${monthly:,.0f}/month expenses
        </p>
    </div>
    """.format(
        status=data['sovereignty_status'],
        ratio=data['sovereignty_ratio'],
        monthly=data['monthly_expenses']
    ), unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Emergency Runway", 
                  f"{data['emergency_runway_months']:.1f} months",
                  "Immediate access only")
    
    with col2:
        st.metric("Bitcoin Holdings",
                  f"{data['total_btc']:.4f} BTC",
                  f"${data['estimated_crypto_value']:,.0f}")
    
    with col3:
        st.metric("Total Net Worth",
                  f"${data['estimated_portfolio_value']:,.0f}",
                  f"At ${data['btc_price']:,.0f}/BTC")
    
    with col4:
        st.metric("Full Sovereignty",
                  f"{data['full_sovereignty_ratio']:.1f}x",
                  "All assets / annual expenses")

# Main page rendering
def render_family_finance_dashboard(username: str, path: str):
    """Main dashboard with setup flow integration"""
    
    # Page header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #dc2626, #991b1b); 
                padding: 20px; 
                border-radius: 10px; 
                margin-bottom: 20px;">
        <h1 style="color: white; margin: 0; text-align: center;">
            🏠 Family Finance Plan
        </h1>
        <p style="color: #fecaca; margin: 10px 0 0 0; text-align: center; font-size: 18px;">
            "Your sovereignty means nothing if your family can't access it when they need it most."
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check setup status
    is_setup_complete = check_user_setup_status(username)
    
    if not is_setup_complete and not st.session_state.get('skip_setup'):
        # Show setup wizard for new users
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info("👋 Welcome! Let's set up your family finance data to calculate your sovereignty metrics.")
            
            if st.button("Start Setup Wizard", type="primary", use_container_width=True):
                st.session_state.show_setup = True
            
            if st.button("Skip for Now", use_container_width=True):
                st.session_state.skip_setup = True
                st.rerun()
        
        if st.session_state.get('show_setup'):
            render_financial_setup_wizard(username, finance_db)
    
    else:
        # Main dashboard for users with data
        
        # Quick update section
        with st.expander("⚡ Quick Updates"):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update Account Balances"):
                    st.session_state.show_quick_update = True
                if st.button("Update Monthly Expenses"):
                    st.session_state.show_expense_update = True
            with col2:
                if st.button("Add New Account"):
                    st.session_state.show_add_account = True
                if st.button("Full Setup Wizard"):
                    st.session_state.show_setup = True
        
        if st.session_state.get('show_quick_update'):
            render_quick_update_form(username, finance_db)
        
        # Calculate metrics with real data
        emergency_data = calculate_enhanced_emergency_metrics(username, path)
        
        # Sovereignty overview
        render_sovereignty_dashboard(emergency_data)
        
        # Main tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🏠 Family Security", 
            "💰 Account Access", 
            "₿ Crypto Recovery", 
            "📋 Planning Tasks",
            "📊 Reports"
        ])
        
        with tab1:
            render_enhanced_emergency_status(emergency_data, username, path)
        
        with tab2:
            render_enhanced_account_matrix(emergency_data, username)
        
        with tab3:
            render_enhanced_crypto_recovery(emergency_data, path)
        
        with tab4:
            render_enhanced_family_planning(username, path)
        
        with tab5:
            render_sovereignty_reports(username, emergency_data)

def render_sovereignty_reports(username: str, data: dict):
    """Financial reports and projections"""
    
    st.markdown("## 📊 Sovereignty Reports & Projections")
    
    # Expense breakdown pie chart
    expense_data = data['expense_breakdown']
    if expense_data['expenses']:
        st.markdown("### 💸 Monthly Expense Breakdown")
        
        # Create pie chart data
        expenses_df = pd.DataFrame([
            {"Category": exp['category'], "Amount": exp['amount']}
            for exp in expense_data['expenses']
        ])
        
        # You can add a pie chart here using plotly or matplotlib
        st.dataframe(expenses_df, hide_index=True)
        
        st.info(f"""
        **Fixed Expenses:** ${expense_data['fixed_total']:,.0f}/month  
        **Variable Expenses:** ${expense_data['variable_total']:,.0f}/month  
        **Total Monthly:** ${expense_data['total_monthly']:,.0f}  
        **Annual Total:** ${expense_data['total_annual']:,.0f}
        """)
    
    # Bitcoin price scenarios
    st.markdown("### ₿ Bitcoin Price Scenarios")
    
    btc_amount = data['total_btc']
    current_price = data['btc_price']
    
    scenarios = {
        "Bear Case": current_price * 0.5,
        "Current": current_price,
        "Conservative": current_price * 2,
        "Optimistic": current_price * 5,
        "Moon": current_price * 10
    }
    
    scenario_data = []
    for scenario, price in scenarios.items():
        btc_value = btc_amount * price
        total_portfolio = data['estimated_portfolio_value'] - data['estimated_crypto_value'] + btc_value
        sovereignty_ratio = btc_value / data['expense_breakdown']['total_annual'] if data['expense_breakdown']['total_annual'] > 0 else 0
        
        scenario_data.append({
            "Scenario": scenario,
            "BTC Price": f"${price:,.0f}",
            "BTC Value": f"${btc_value:,.0f}",
            "Total Portfolio": f"${total_portfolio:,.0f}",
            "Sovereignty Years": f"{sovereignty_ratio:.1f}"
        })
    
    st.dataframe(pd.DataFrame(scenario_data), hide_index=True, use_container_width=True)
    
    # Historical snapshot tracking
    st.markdown("### 📈 Sovereignty Progress")
    st.info("Track your sovereignty ratio over time as you stack sats and reduce expenses")

# Run the dashboard
if __name__ == "__main__":
    render_family_finance_dashboard(username, path)