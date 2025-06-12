# pages/6_Family_Emergency.py
import streamlit as st
import pandas as pd
import json
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import from project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection

# Get username and path from query params or session state
username = st.query_params.get("username", None) or st.session_state.get("username", None)
path = st.query_params.get("path", None) or st.session_state.get("path", None)

if not username or not path:
    st.error("❌ Please log in through the main dashboard first")
    st.stop()

def render_family_emergency_dashboard(username, path):
    """
    Family Emergency Dashboard - MVP Implementation
    Transforms sovereignty data into family-accessible emergency planning
    """
    
    # Page Header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #dc2626, #991b1b); 
                padding: 20px; 
                border-radius: 10px; 
                margin-bottom: 20px;">
        <h1 style="color: white; margin: 0; text-align: center;">
            🚨 Family Emergency Dashboard
        </h1>
        <p style="color: #fecaca; margin: 10px 0 0 0; text-align: center; font-size: 18px;">
            "Your sovereignty means nothing if your family can't access it when they need it most."
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get user data for calculations
    emergency_data = calculate_emergency_metrics(username, path)
    
    if "error" in emergency_data:
        st.error(f"❌ {emergency_data['error']}")
        return
    
    # Top Status Overview
    render_emergency_status_overview(emergency_data)
    
    # Main Content Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏠 Emergency Status", 
        "💰 Account Access", 
        "₿ Crypto Recovery", 
        "📋 Family Planning"
    ])
    
    with tab1:
        render_emergency_status_detailed(emergency_data, username, path)
    
    with tab2:
        render_account_access_matrix(emergency_data, username)
    
    with tab3:
        render_crypto_recovery_protocol(emergency_data, path)
    
    with tab4:
        render_family_planning_tools(username, path)

def calculate_emergency_metrics(username, path):
    """Calculate emergency preparedness metrics from existing sovereignty data"""
    try:
        with get_db_connection() as conn:
            # Get recent sovereignty data
            recent_data = conn.execute("""
                SELECT timestamp, score, btc_usd, btc_sats, home_cooked_meals, 
                       no_spending, invested_bitcoin, meditation, gratitude
                FROM sovereignty 
                WHERE username = ? 
                ORDER BY timestamp DESC 
                LIMIT 90
            """, [username]).fetchall()
            
            if not recent_data:
                return {"error": "No sovereignty data found. Track some habits first!"}
            
            # Calculate metrics
            total_btc_invested = sum(row[2] for row in recent_data if row[2])
            total_sats = sum(row[3] for row in recent_data if row[3])
            avg_score = sum(row[1] for row in recent_data if row[1]) / len(recent_data)
            
            # Estimate portfolio value (using your PowerBI as reference)
            estimated_crypto_value = total_sats * 0.001 + total_btc_invested  # Rough estimate
            estimated_total_portfolio = estimated_crypto_value * 2.7  # Based on your 40% crypto allocation
            
            # Emergency calculations
            monthly_expenses = 5000  # Based on your PowerBI budget
            emergency_runway_months = estimated_total_portfolio / monthly_expenses
            
            return {
                "username": username,
                "path": path,
                "emergency_runway_months": emergency_runway_months,
                "estimated_portfolio_value": estimated_total_portfolio,
                "estimated_crypto_value": estimated_crypto_value,
                "avg_sovereignty_score": avg_score,
                "total_btc_invested": total_btc_invested,
                "total_sats": total_sats,
                "monthly_expenses": monthly_expenses,
                "immediate_access_estimate": estimated_total_portfolio * 0.15,  # Joint accounts
                "short_term_access_estimate": estimated_crypto_value,  # Crypto recovery
                "sovereignty_status": get_sovereignty_status(emergency_runway_months)
            }
            
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}

def get_sovereignty_status(runway_months):
    """Convert runway months to sovereignty status"""
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

def render_emergency_status_overview(data):
    """Top-level emergency status cards"""
    
    status = data["sovereignty_status"]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {status['color']}20, {status['color']}10); 
                    border: 2px solid {status['color']}; 
                    border-radius: 10px; 
                    padding: 20px; 
                    text-align: center;">
            <h3 style="margin: 0; color: {status['color']};">{status['icon']} {status['level']}</h3>
            <p style="margin: 5px 0 0 0; color: #6b7280;">Emergency Status</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        runway_months = data["emergency_runway_months"]
        st.markdown(f"""
        <div style="background: rgba(59, 130, 246, 0.1); 
                    border: 2px solid #3b82f6; 
                    border-radius: 10px; 
                    padding: 20px; 
                    text-align: center;">
            <h3 style="margin: 0; color: #3b82f6;">{runway_months:.1f} months</h3>
            <p style="margin: 5px 0 0 0; color: #6b7280;">Emergency Runway</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        immediate_access = data["immediate_access_estimate"]
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.1); 
                    border: 2px solid #10b981; 
                    border-radius: 10px; 
                    padding: 20px; 
                    text-align: center;">
            <h3 style="margin: 0; color: #10b981;">${immediate_access:,.0f}</h3>
            <p style="margin: 5px 0 0 0; color: #6b7280;">Immediate Access</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        preparedness_score = min(100, (data["avg_sovereignty_score"] / 100) * 100)
        st.markdown(f"""
        <div style="background: rgba(139, 92, 246, 0.1); 
                    border: 2px solid #8b5cf6; 
                    border-radius: 10px; 
                    padding: 20px; 
                    text-align: center;">
            <h3 style="margin: 0; color: #8b5cf6;">{preparedness_score:.0f}%</h3>
            <p style="margin: 5px 0 0 0; color: #6b7280;">Family Preparedness</p>
        </div>
        """, unsafe_allow_html=True)

def render_emergency_status_detailed(data, username, path):
    """Detailed emergency status and action items"""
    
    st.markdown("## 🎯 Emergency Action Plan")
    
    runway_months = data["emergency_runway_months"]
    
    if runway_months >= 36:  # 3+ years
        st.success("✅ **SECURE STATUS** - Your family has strong financial protection.")
        st.markdown("""
        **Immediate Priority:** Optimize emergency access procedures and train family members.
        
        **Next Steps:**
        - Document all account locations and access methods
        - Schedule quarterly family financial meetings  
        - Set up crypto recovery protocols
        - Consider advanced estate planning
        """)
    
    elif runway_months >= 12:  # 1-3 years
        st.warning("⚠️ **STABLE STATUS** - Good foundation, some optimization needed.")
        st.markdown("""
        **Immediate Priority:** Strengthen emergency fund and improve access procedures.
        
        **Next Steps:**
        - Increase liquid emergency savings to 6+ months
        - Document crypto access procedures immediately
        - Review and optimize monthly expenses
        - Begin family financial education
        """)
    
    else:  # <1 year
        st.error("🚨 **ACTION NEEDED** - Immediate steps required for family security.")
        st.markdown("""
        **URGENT PRIORITY:** Build emergency fund and document all access methods NOW.
        
        **This Week:**
        - List all accounts and their access requirements
        - Set up emergency contact list with account information
        - Begin aggressive expense reduction
        - Consider liquidating non-essential assets
        """)
    
    # Emergency Timeline
    st.markdown("### ⏰ Emergency Timeline")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**If emergency happened TODAY:**")
        st.markdown(f"""
        - **Month 1-3:** Use immediate access funds (${data['immediate_access_estimate']:,.0f})
        - **Month 4-6:** Access crypto/investments (${data['short_term_access_estimate']:,.0f})
        - **Month 7+:** Long-term asset liquidation if needed
        """)
    
    with col2:
        st.markdown("**Critical Documents Needed:**")
        st.markdown("""
        - [ ] Death certificates (order 10+ copies)
        - [ ] Social Security notification
        - [ ] Insurance policy claims
        - [ ] Bank/investment account access
        - [ ] Crypto wallet recovery procedures
        """)

def render_account_access_matrix(data, username):
    """Account access priority matrix"""
    
    st.markdown("## 💳 Account Access Priority Matrix")
    st.markdown("*Accounts listed by speed of access in emergency situations*")
    
    # Create sample account data based on user's situation
    immediate_accounts = [
        {"Account": "Joint Checking", "Balance": "$12,530", "Access": "Existing debit card/online", "Time": "Immediate"},
        {"Account": "Joint Savings", "Balance": "$35,000", "Access": "Online banking", "Time": "Immediate"},
        {"Account": "Emergency Fund CD", "Balance": "$15,000", "Access": "Bank visit", "Time": "1-2 days"}
    ]
    
    short_term_accounts = [
        {"Account": "Crypto Portfolio", "Balance": f"${data['estimated_crypto_value']:,.0f}", "Access": "Hardware wallet recovery", "Time": "2-7 days"},
        {"Account": "Investment Account", "Balance": "$45,000", "Access": "Brokerage call", "Time": "3-5 days"},
        {"Account": "Life Insurance", "Balance": "$250,000", "Access": "Policy claim", "Time": "7-14 days"}
    ]
    
    long_term_accounts = [
        {"Account": "401k/IRA", "Balance": "$150,000", "Access": "HR/Plan admin", "Time": "14-30 days"},
        {"Account": "Home Equity", "Balance": "$200,000", "Access": "HELOC/Sale", "Time": "30+ days"},
        {"Account": "Other Investments", "Balance": "$50,000", "Access": "Estate process", "Time": "30+ days"}
    ]
    
    # Display tables
    st.markdown("### 🟢 IMMEDIATE ACCESS (0-24 hours)")
    st.dataframe(pd.DataFrame(immediate_accounts), hide_index=True, use_container_width=True)
    
    st.markdown("### 🟡 SHORT-TERM ACCESS (1-14 days)")
    st.dataframe(pd.DataFrame(short_term_accounts), hide_index=True, use_container_width=True)
    
    st.markdown("### 🔴 LONG-TERM ACCESS (2+ weeks)")
    st.dataframe(pd.DataFrame(long_term_accounts), hide_index=True, use_container_width=True)
    
    # Emergency Contact Widget
    st.markdown("### 📞 Emergency Financial Contacts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Emergency Contacts", key="save_contacts"):
            st.session_state.emergency_contacts_saved = True
        
        primary_contact = st.text_input("Primary Financial Advisor", 
                                       value=st.session_state.get("primary_advisor", ""),
                                       placeholder="Name, Phone, Email")
        
        attorney_contact = st.text_input("Estate Attorney", 
                                        value=st.session_state.get("estate_attorney", ""),
                                        placeholder="Name, Phone, Email")
    
    with col2:
        insurance_contact = st.text_input("Insurance Agent", 
                                         value=st.session_state.get("insurance_agent", ""),
                                         placeholder="Name, Phone, Email")
        
        family_contact = st.text_input("Trusted Family Member", 
                                      value=st.session_state.get("family_contact", ""),
                                      placeholder="Name, Phone, Relationship")
    
    if st.session_state.get("emergency_contacts_saved"):
        st.success("✅ Emergency contacts saved to session (will be permanent once database schema is added)")

def render_crypto_recovery_protocol(data, path):
    """Crypto-specific recovery procedures"""
    
    st.markdown("## ₿ Cryptocurrency Recovery Protocol")
    
    if data["estimated_crypto_value"] < 1000:
        st.info("💡 You have minimal crypto holdings. Focus on traditional account access first.")
        return
    
    st.markdown(f"""
    **Your Crypto Holdings:** ~${data['estimated_crypto_value']:,.0f}
    **Recovery Priority:** HIGH (significant value requires immediate documentation)
    """)
    
    # Recovery Steps
    st.markdown("### 🔐 Step-by-Step Recovery Process")
    
    recovery_steps = [
        {
            "step": "1. Locate Hardware Wallet",
            "description": "Find physical hardware wallet device",
            "location": "Safe deposit box / Home safe",
            "urgent": True
        },
        {
            "step": "2. Find Recovery Phrase", 
            "description": "Locate 12/24 word seed phrase backup",
            "location": "Sealed envelope / Safe deposit box",
            "urgent": True
        },
        {
            "step": "3. Install Wallet Software",
            "description": "Download official wallet software",
            "location": "Computer/Phone app store",
            "urgent": False
        },
        {
            "step": "4. Recovery Process",
            "description": "Enter seed phrase to restore wallet",
            "location": "At home computer (NEVER online)",
            "urgent": False
        },
        {
            "step": "5. Verify Balances",
            "description": "Confirm all crypto assets are accessible",
            "location": "Wallet interface",
            "urgent": False
        }
    ]
    
    for step in recovery_steps:
        urgency_color = "#dc2626" if step["urgent"] else "#6b7280"
        st.markdown(f"""
        <div style="border-left: 4px solid {urgency_color}; 
                    padding: 12px; 
                    margin: 8px 0; 
                    background: rgba(156, 163, 175, 0.1);">
            <strong style="color: {urgency_color};">{step['step']}</strong><br>
            {step['description']}<br>
            <em>Location: {step['location']}</em>
        </div>
        """, unsafe_allow_html=True)
    
    # Crypto Emergency Contacts
    st.markdown("### 👥 Crypto-Specific Emergency Contacts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Crypto Mentor/Expert", 
                     placeholder="Trusted person who understands crypto")
        st.text_input("Hardware Wallet Support", 
                     placeholder="Ledger/Trezor customer support")
    
    with col2:
        st.text_input("Crypto-Savvy Family Member", 
                     placeholder="Family member with crypto knowledge")
        st.text_input("Local Bitcoin Community", 
                     placeholder="Local meetup or Bitcoin group")
    
    # Critical Warnings
    st.markdown("### ⚠️ CRITICAL WARNINGS")
    st.error("""
    **NEVER:**
    - Enter seed phrases on websites or apps you don't trust
    - Send photos of seed phrases via text/email
    - Panic sell during market volatility
    
    **ALWAYS:**
    - Test recovery process while owner is still alive
    - Keep multiple physical backups in separate locations
    - Sell in small chunks (25% max) to avoid market impact
    """)

def render_family_planning_tools(username, path):
    """Family planning and training tools"""
    
    st.markdown("## 📋 Family Financial Education & Planning")
    
    # Family Training Checklist
    st.markdown("### 👨‍👩‍👧‍👦 Family Training Checklist")
    
    training_items = [
        {"task": "Basic financial account overview", "frequency": "Monthly", "completed": False},
        {"task": "Emergency contact list review", "frequency": "Quarterly", "completed": False},
        {"task": "Crypto basics explanation", "frequency": "One-time", "completed": False},
        {"task": "Document location walkthrough", "frequency": "Bi-annually", "completed": False},
        {"task": "Emergency budget planning", "frequency": "Annually", "completed": False},
        {"task": "Insurance policy review", "frequency": "Annually", "completed": False}
    ]
    
    for i, item in enumerate(training_items):
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            completed = st.checkbox("", key=f"training_{i}", value=item["completed"])
        
        with col2:
            st.markdown(f"**{item['task']}**")
        
        with col3:
            st.markdown(f"*{item['frequency']}*")
    
    # Family Meeting Scheduler
    st.markdown("### 📅 Family Financial Meeting Planner")
    
    col1, col2 = st.columns(2)
    
    with col1:
        next_meeting = st.date_input("Next Family Meeting", 
                                    value=datetime.now() + timedelta(days=30))
        meeting_agenda = st.text_area("Meeting Agenda", 
                                     placeholder="Topics to discuss...")
    
    with col2:
        st.markdown("**Suggested Agenda Items:**")
        st.markdown("""
        - Review account access procedures
        - Update emergency contact information
        - Discuss any new financial accounts
        - Practice crypto recovery steps
        - Review monthly budget and expenses
        - Update beneficiary information
        """)
    
    if st.button("📝 Schedule Family Meeting"):
        st.success(f"✅ Family meeting scheduled for {next_meeting}")
        st.session_state.family_meeting_scheduled = True
    
    # Document Location Tracker
    st.markdown("### 📁 Important Document Locations")
    
    documents = [
        "Will & Trust Documents",
        "Insurance Policies", 
        "Investment Account Statements",
        "Crypto Recovery Information",
        "Tax Returns (Last 3 Years)",
        "Property Deeds",
        "Social Security Cards",
        "Birth Certificates"
    ]
    
    col1, col2 = st.columns(2)
    
    for i, doc in enumerate(documents):
        col = col1 if i % 2 == 0 else col2
        with col:
            location = st.text_input(doc, 
                                   placeholder="Location/Details",
                                   key=f"doc_{i}")
    
    # Family Preparedness Score
    st.markdown("### 🎯 Family Preparedness Score")
    
    completed_items = sum(1 for i in range(len(training_items)) 
                         if st.session_state.get(f"training_{i}", False))
    preparedness_percentage = (completed_items / len(training_items)) * 100
    
    progress_color = "#10b981" if preparedness_percentage >= 80 else "#eab308" if preparedness_percentage >= 50 else "#dc2626"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {progress_color}20, {progress_color}10); 
                border: 2px solid {progress_color}; 
                border-radius: 10px; 
                padding: 20px; 
                text-align: center;">
        <h2 style="margin: 0; color: {progress_color};">{preparedness_percentage:.0f}%</h2>
        <p style="margin: 5px 0 0 0; color: #6b7280;">Family Preparedness Complete</p>
    </div>
    """, unsafe_allow_html=True)

# Call the main function with user data
render_family_emergency_dashboard(username, path)