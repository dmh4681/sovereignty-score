# improved_emergency_features.py
# Enhanced calculations and better tab content

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def calculate_real_family_preparedness(user_data, path, session_state):
    """
    Calculate REAL family preparedness including actual emergency tasks
    Not just sovereignty habits - actual emergency planning completion
    """
    
    # Sovereignty habit consistency (foundation)
    recent_data = user_data[:30]  # Last 30 days
    habit_scores = {
        "meditation_consistency": sum(1 for row in recent_data if row[7]) / len(recent_data),
        "gratitude_consistency": sum(1 for row in recent_data if row[8]) / len(recent_data),
        "learning_consistency": sum(1 for row in recent_data if row[9]) / len(recent_data),
        "spending_discipline": sum(1 for row in recent_data if row[5]) / len(recent_data),
        "investment_consistency": sum(1 for row in recent_data if row[6]) / len(recent_data)
    }
    sovereignty_foundation = sum(habit_scores.values()) / len(habit_scores)
    
    # ACTUAL emergency preparedness tasks (from session state)
    emergency_tasks = {
        "emergency_contacts_saved": bool(session_state.get("emergency_contacts_saved", False)),
        "training_checklist_progress": calculate_training_progress(session_state),
        "document_locations_filled": calculate_document_progress(session_state),
        "family_meeting_scheduled": bool(session_state.get("family_meeting_scheduled", False)),
        "crypto_contacts_saved": calculate_crypto_contacts_progress(session_state)
    }
    
    # Calculate actual task completion
    tasks_completed = sum(emergency_tasks.values()) / len(emergency_tasks)
    
    # Weighted family preparedness calculation
    real_preparedness = (
        tasks_completed * 0.70 +           # 70% weight for actual emergency tasks
        sovereignty_foundation * 0.30      # 30% for sovereignty habit foundation
    )
    
    return {
        "family_preparedness_score": real_preparedness * 100,
        "sovereignty_foundation": sovereignty_foundation * 100,
        "emergency_tasks_completion": tasks_completed * 100,
        "task_breakdown": emergency_tasks,
        "habit_foundation": habit_scores,
        "preparedness_level": get_preparedness_level(real_preparedness * 100)
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

def calculate_training_progress(session_state):
    """Calculate family training checklist progress"""
    training_items = [
        "training_0", "training_1", "training_2", 
        "training_3", "training_4", "training_5"
    ]
    completed = sum(1 for item in training_items if session_state.get(item, False))
    return completed / len(training_items)

def calculate_document_progress(session_state):
    """Calculate document location completion"""
    document_items = [f"doc_{i}" for i in range(8)]  # 8 document types
    filled = sum(1 for item in document_items 
                if session_state.get(item, "") and len(session_state.get(item, "").strip()) > 0)
    return filled / len(document_items)

def calculate_crypto_contacts_progress(session_state):
    """Calculate crypto emergency contacts completion"""
    crypto_contacts = ["crypto_mentor", "hardware_support", "crypto_family", "bitcoin_community"]
    filled = sum(1 for contact in crypto_contacts 
                if session_state.get(contact, "") and len(session_state.get(contact, "").strip()) > 0)
    return filled / len(crypto_contacts)

def render_enhanced_emergency_status(data, username, path):
    """Enhanced Emergency Status tab with real preparedness breakdown"""
    
    st.markdown("## 🎯 Emergency Action Plan")
    
    runway_months = data["emergency_runway_months"]
    
    # Action plan based on actual status
    if runway_months >= 36:  # 3+ years
        st.success("✅ **SECURE STATUS** - Your family has strong financial protection.")
        action_priority = "OPTIMIZE"
        action_description = "Focus on emergency access procedures and family training."
    elif runway_months >= 12:  # 1-3 years
        st.warning("⚠️ **STABLE STATUS** - Good foundation, some optimization needed.")
        action_priority = "STRENGTHEN"
        action_description = "Increase emergency fund and improve access procedures."
    else:  # <1 year
        st.error("🚨 **ACTION NEEDED** - Immediate steps required for family security.")
        action_priority = "BUILD"
        action_description = "Build emergency fund and document all access methods NOW."
    
    # Enhanced preparedness breakdown
    if "preparedness_details" in data:
        prep_data = data["preparedness_details"]
        
        st.markdown("### 📊 Family Preparedness Breakdown")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            foundation_score = prep_data.get("sovereignty_foundation", 0)
            st.metric("Sovereignty Foundation", f"{foundation_score:.0f}%", 
                     help="Based on your daily sovereignty habits")
        
        with col2:
            tasks_score = prep_data.get("emergency_tasks_completion", 0)
            st.metric("Emergency Tasks", f"{tasks_score:.0f}%", 
                     help="Actual emergency preparedness tasks completed")
        
        with col3:
            overall_score = prep_data.get("family_preparedness_score", 0)
            color = "#10b981" if overall_score >= 70 else "#eab308" if overall_score >= 40 else "#dc2626"
            st.markdown(f"""
            <div style="text-align: center; padding: 10px;">
                <h2 style="color: {color}; margin: 0;">{overall_score:.0f}%</h2>
                <p style="margin: 5px 0 0 0; color: #6b7280;">Overall Preparedness</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Task completion details
        st.markdown("### ✅ Task Completion Status")
        task_breakdown = prep_data.get("task_breakdown", {})
        
        for task_name, completed in task_breakdown.items():
            status_icon = "✅" if completed else "❌"
            task_display = task_name.replace("_", " ").title()
            st.markdown(f"{status_icon} **{task_display}**: {'Completed' if completed else 'Not Started'}")
    
    # Priority action items
    st.markdown("### 🚨 Priority Actions This Week")
    
    if action_priority == "BUILD":
        st.markdown("""
        **URGENT (Do This Week):**
        - [ ] Complete emergency contact information below
        - [ ] Document all crypto wallet locations and recovery procedures  
        - [ ] Schedule first family financial meeting
        - [ ] Calculate exact monthly minimum expenses
        - [ ] List all accounts and their access requirements
        """)
    elif action_priority == "STRENGTHEN":
        st.markdown("""
        **HIGH PRIORITY (Do This Month):**
        - [ ] Complete family training checklist items
        - [ ] Document all account access procedures
        - [ ] Test crypto recovery procedures with family
        - [ ] Schedule quarterly family financial meetings
        - [ ] Optimize expense reduction strategies
        """)
    else:  # OPTIMIZE
        st.markdown("""
        **OPTIMIZATION (Next Quarter):**
        - [ ] Complete advanced family training modules
        - [ ] Set up emergency drill schedules
        - [ ] Consider advanced estate planning consultation
        - [ ] Implement automated emergency notification systems
        - [ ] Document succession planning for business/investments
        """)

def render_enhanced_crypto_recovery(data, path):
    """Enhanced crypto recovery with real tracking integration"""
    
    st.markdown("## ₿ Cryptocurrency Recovery Protocol")
    
    crypto_value = data.get("estimated_crypto_value", 0)
    total_sats = data.get("total_sats", 0)
    btc_invested = data.get("total_btc_invested", 0)
    
    if crypto_value < 1000:
        st.info("💡 You have minimal crypto holdings. Focus on traditional account access first.")
        return
    
    # Real crypto portfolio display
    st.markdown(f"""
    ### 📊 Your Actual Crypto Position
    **Total Bitcoin Invested:** ${btc_invested:,.2f}  
    **Total Sats Accumulated:** {total_sats:,} sats  
    **Estimated Current Value:** ${crypto_value:,.0f}  
    **Recovery Priority:** {'HIGH' if crypto_value > 10000 else 'MEDIUM'} (significant value requires immediate documentation)
    """)
    
    # Path-specific crypto advice
    if path == "financial_path":
        st.warning("🎯 **Financial Path Alert:** Your crypto holdings are central to your sovereignty strategy. Recovery procedures are CRITICAL.")
    
    # Enhanced recovery checklist with real consequences
    st.markdown("### 🔐 Critical Recovery Checklist")
    
    recovery_items = [
        {
            "task": "Hardware wallet location documented",
            "urgency": "CRITICAL",
            "consequence": f"${crypto_value:,.0f} permanently lost if wallet is misplaced",
            "session_key": "hw_wallet_location"
        },
        {
            "task": "Seed phrase backup verified and documented", 
            "urgency": "CRITICAL",
            "consequence": "Complete loss of funds if seed phrase is lost or damaged",
            "session_key": "seed_phrase_location"
        },
        {
            "task": "Family member trained on recovery process",
            "urgency": "HIGH", 
            "consequence": "Family cannot access funds even with proper documentation",
            "session_key": "family_crypto_trained"
        },
        {
            "task": "Crypto emergency contacts established",
            "urgency": "MEDIUM",
            "consequence": "No expert help available during recovery emergency",
            "session_key": "crypto_contacts_done"
        }
    ]
    
    for item in recovery_items:
        urgency_color = "#dc2626" if item["urgency"] == "CRITICAL" else "#f97316" if item["urgency"] == "HIGH" else "#eab308"
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            completed = st.checkbox("", key=item["session_key"], 
                                  help=f"Mark when {item['task'].lower()} is complete")
        
        with col2:
            status_text = "✅ COMPLETED" if completed else f"❌ {item['urgency']}"
            st.markdown(f"""
            <div style="border-left: 4px solid {urgency_color}; padding: 10px; margin: 5px 0;">
                <strong>{item['task']}</strong> - {status_text}<br>
                <em style="color: #6b7280;">Risk: {item['consequence']}</em>
            </div>
            """, unsafe_allow_html=True)
    
    # Crypto-specific emergency contacts with session persistence
    st.markdown("### 👥 Crypto Emergency Contacts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        crypto_mentor = st.text_input("Crypto Mentor/Expert", 
                     value=st.session_state.get("crypto_mentor", ""),
                     placeholder="Trusted person who understands crypto recovery")
        st.session_state["crypto_mentor"] = crypto_mentor
        
        hardware_support = st.text_input("Hardware Wallet Support", 
                     value=st.session_state.get("hardware_support", ""),
                     placeholder="Ledger/Trezor customer support info")
        st.session_state["hardware_support"] = hardware_support
    
    with col2:
        crypto_family = st.text_input("Crypto-Savvy Family Member", 
                     value=st.session_state.get("crypto_family", ""),
                     placeholder="Family member with crypto knowledge")
        st.session_state["crypto_family"] = crypto_family
        
        bitcoin_community = st.text_input("Local Bitcoin Community", 
                     value=st.session_state.get("bitcoin_community", ""),
                     placeholder="Local meetup or Bitcoin group contact")
        st.session_state["bitcoin_community"] = bitcoin_community
    
    # Save progress
    if st.button("💾 Save Crypto Recovery Information"):
        st.session_state["crypto_recovery_saved"] = True
        st.success("✅ Crypto recovery information saved!")
    
    # Enhanced warnings with real dollar amounts
    st.markdown("### ⚠️ CRITICAL RECOVERY WARNINGS")
    st.error(f"""
    **NEVER FORGET:**
    - Your ${crypto_value:,.0f} in crypto could be permanently lost
    - No bank or customer service can recover lost crypto
    - Test recovery procedures while you're still alive
    - Keep seed phrases OFFLINE and in multiple secure locations
    
    **SELLING STRATEGY:**
    - Sell maximum 25% at once to avoid market impact
    - Your {total_sats:,} sats = significant position, sell carefully
    - Wait for family member guidance before panic selling
    """)

def render_enhanced_family_planning(username, path):
    """Enhanced family planning with progress tracking"""
    
    st.markdown("## 📋 Family Financial Education & Planning")
    
    # Enhanced training checklist with better progress tracking
    st.markdown("### 👨‍👩‍👧‍👦 Family Training Progress")
    
    training_items = [
        {"task": "Basic financial account overview", "frequency": "Monthly", "importance": "Foundation"},
        {"task": "Emergency contact list review", "frequency": "Quarterly", "importance": "Critical"},
        {"task": "Crypto basics explanation", "frequency": "One-time", "importance": "High"},
        {"task": "Document location walkthrough", "frequency": "Bi-annually", "importance": "Critical"},
        {"task": "Emergency budget planning", "frequency": "Annually", "importance": "Medium"},
        {"task": "Insurance policy review", "frequency": "Annually", "importance": "High"}
    ]
    
    completed_count = 0
    
    for i, item in enumerate(training_items):
        col1, col2, col3, col4 = st.columns([0.5, 3, 1, 1])
        
        with col1:
            completed = st.checkbox("", key=f"training_{i}", value=False)
            if completed:
                completed_count += 1
        
        with col2:
            status_color = "#10b981" if completed else "#6b7280"
            st.markdown(f"<span style='color: {status_color};'><strong>{item['task']}</strong></span>", 
                       unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"*{item['frequency']}*")
        
        with col4:
            importance_color = "#dc2626" if item['importance'] == "Critical" else "#f97316" if item['importance'] == "High" else "#eab308"
            st.markdown(f"<span style='color: {importance_color};'>{item['importance']}</span>", 
                       unsafe_allow_html=True)
    
    # Progress visualization
    progress_percentage = (completed_count / len(training_items)) * 100
    progress_color = "#10b981" if progress_percentage >= 80 else "#eab308" if progress_percentage >= 50 else "#dc2626"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {progress_color}20, {progress_color}10); 
                border: 2px solid {progress_color}; 
                border-radius: 10px; 
                padding: 20px; 
                text-align: center;
                margin: 20px 0;">
        <h2 style="margin: 0; color: {progress_color};">{progress_percentage:.0f}%</h2>
        <p style="margin: 5px 0 0 0; color: #6b7280;">Family Training Complete ({completed_count}/{len(training_items)} tasks)</p>
    </div>
    """, unsafe_allow_html=True)
    
    if progress_percentage < 50:
        st.warning("⚠️ **Less than 50% family training complete.** Priority: Schedule family meeting to cover critical items.")
    elif progress_percentage < 80:
        st.info("📈 **Good progress!** Focus on completing the remaining high-importance items.")
    else:
        st.success("🎉 **Excellent family preparedness!** Your family is well-prepared for emergencies.")

# Update the main emergency metrics function to use real preparedness
def get_enhanced_emergency_data(username, path):
    """Enhanced emergency data with real preparedness calculations"""
    from real_emergency_calculator import calculate_real_emergency_metrics
    
    # Get the base data
    base_data = calculate_real_emergency_metrics(username, path)
    
    if "error" in base_data:
        return base_data
    
    # Get user data for enhanced preparedness calculation
    try:
        from db import get_db_connection
        with get_db_connection() as conn:
            user_data = conn.execute("""
                SELECT timestamp, score, btc_usd, btc_sats, home_cooked_meals,
                       no_spending, invested_bitcoin, meditation, gratitude,
                       read_or_learned, environmental_action, exercise_minutes,
                       strength_training, junk_food
                FROM sovereignty 
                WHERE username = ? 
                ORDER BY timestamp DESC 
                LIMIT 180
            """, [username]).fetchall()
        
        # Calculate REAL family preparedness
        real_preparedness = calculate_real_family_preparedness(user_data, path, st.session_state)
        
        # Update the preparedness details
        base_data["preparedness_analysis"] = real_preparedness
        
        # Transform to match dashboard expectations
        financial = base_data["financial_position"]
        expenses = base_data["expense_analysis"]
        accounts = base_data["account_access_matrix"]
        
        return {
            "username": username,
            "path": path,
            "emergency_runway_months": base_data["emergency_runway_months"],
            "estimated_portfolio_value": financial["total_assets"],
            "estimated_crypto_value": financial["current_crypto_value"],
            "avg_sovereignty_score": real_preparedness["sovereignty_foundation"],
            "total_btc_invested": financial["total_btc_invested"],
            "total_sats": financial["total_sats"],
            "monthly_expenses": expenses["monthly_expenses"],
            "immediate_access_estimate": accounts["total_immediate"],
            "short_term_access_estimate": accounts["total_short_term"],
            "sovereignty_status": base_data["sovereignty_status"],
            "detailed_accounts": accounts,
            "expense_breakdown": expenses,
            "preparedness_details": real_preparedness,
            "data_quality": base_data["data_quality"]
        }
        
    except Exception as e:
        return {"error": f"Enhanced calculation error: {str(e)}"}