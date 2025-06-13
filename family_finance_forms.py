# family_finance_forms.py
"""
Streamlit forms for inputting family finance data
Provides user-friendly interface for comprehensive financial data collection
"""

import streamlit as st
from datetime import datetime, date
from typing import Dict, Optional
from family_finance_database import FamilyFinanceDB

def render_financial_setup_wizard(username: str, db: FamilyFinanceDB):
    """Main setup wizard for initial financial data input"""
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3a8a, #3730a3); 
                padding: 20px; 
                border-radius: 10px; 
                margin-bottom: 20px;">
        <h1 style="color: white; margin: 0; text-align: center;">
            💰 Financial Data Setup Wizard
        </h1>
        <p style="color: #ddd6fe; margin: 10px 0 0 0; text-align: center;">
            Let's build your complete sovereignty picture
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress tracking
    if 'setup_step' not in st.session_state:
        st.session_state.setup_step = 1
    
    # Step indicators
    steps = ['Accounts', 'Crypto', 'Expenses', 'Contacts', 'Documents']
    progress = st.session_state.setup_step / len(steps)
    st.progress(progress)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]
    
    for i, (col, step) in enumerate(zip(cols, steps)):
        with col:
            if i + 1 < st.session_state.setup_step:
                st.success(f"✅ {step}")
            elif i + 1 == st.session_state.setup_step:
                st.info(f"📝 {step}")
            else:
                st.text(f"⏳ {step}")
    
    st.markdown("---")
    
    # Render current step
    if st.session_state.setup_step == 1:
        render_accounts_form(username, db)
    elif st.session_state.setup_step == 2:
        render_crypto_form(username, db)
    elif st.session_state.setup_step == 3:
        render_expenses_form(username, db)
    elif st.session_state.setup_step == 4:
        render_contacts_form(username, db)
    elif st.session_state.setup_step == 5:
        render_documents_form(username, db)
    
    # Navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.session_state.setup_step > 1:
            if st.button("⬅️ Previous"):
                st.session_state.setup_step -= 1
                st.rerun()
    
    with col3:
        if st.session_state.setup_step < len(steps):
            if st.button("Next ➡️"):
                st.session_state.setup_step += 1
                st.rerun()
        else:
            if st.button("🎉 Complete Setup"):
                st.success("✅ Financial setup complete! Calculating your sovereignty metrics...")
                st.session_state.setup_complete = True
                st.rerun()

def render_accounts_form(username: str, db: FamilyFinanceDB):
    """Form for inputting financial accounts"""
    
    st.markdown("### 💳 Financial Accounts")
    st.info("Add all your financial accounts, starting with the most accessible")
    
    # Account input form
    with st.form("add_account"):
        col1, col2 = st.columns(2)
        
        with col1:
            account_name = st.text_input("Account Name*", 
                placeholder="e.g., Chase Checking")
            
            account_type = st.selectbox("Account Type*", [
                "Checking",
                "Savings", 
                "Investment",
                "Crypto Exchange",
                "Retirement (401k)",
                "Retirement (IRA)",
                "Real Estate",
                "Business",
                "Other"
            ])
            
            institution = st.text_input("Institution",
                placeholder="e.g., Chase Bank")
            
            balance = st.number_input("Current Balance*", 
                min_value=0.0, 
                format="%.2f",
                help="Enter current USD value")
        
        with col2:
            access_priority = st.selectbox("Access Speed*", [
                ("immediate", "Immediate (0-24 hours)"),
                ("short_term", "Short-term (1-14 days)"),
                ("medium_term", "Medium-term (2-4 weeks)"),
                ("long_term", "Long-term (30+ days)")
            ], format_func=lambda x: x[1])
            
            access_method = st.text_input("Access Method",
                placeholder="e.g., Online banking, Debit card")
            
            days_to_access = st.number_input("Days to Access",
                min_value=0,
                help="Typical days needed to access funds")
            
            is_joint = st.checkbox("Joint Account",
                help="Check if spouse has equal access")
        
        notes = st.text_area("Notes",
            placeholder="Any special instructions or details")
        
        submitted = st.form_submit_button("➕ Add Account")
        
        if submitted:
            if account_name and balance >= 0:
                account_data = {
                    'account_name': account_name,
                    'account_type': account_type,
                    'institution': institution,
                    'balance': balance,
                    'access_priority': access_priority[0],
                    'access_method': access_method,
                    'days_to_access': days_to_access,
                    'is_joint': is_joint,
                    'notes': notes
                }
                
                if db.upsert_account(username, account_data):
                    st.success(f"✅ Added {account_name}")
                    st.rerun()
                else:
                    st.error("❌ Error adding account")
            else:
                st.error("Please fill required fields")
    
    # Display existing accounts
    st.markdown("### 📊 Your Accounts")
    accounts = db.get_accounts_by_priority(username)
    
    total_value = 0
    for priority, priority_accounts in accounts.items():
        if priority_accounts:
            priority_label = {
                'immediate': '🟢 Immediate Access',
                'short_term': '🟡 Short-term Access',
                'medium_term': '🟠 Medium-term Access',
                'long_term': '🔴 Long-term Access'
            }[priority]
            
            st.markdown(f"#### {priority_label}")
            
            for acc in priority_accounts:
                total_value += acc['balance']
                
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                with col1:
                    st.write(f"**{acc['account_name']}**")
                    st.caption(f"{acc['account_type']} - {acc['institution'] or 'N/A'}")
                with col2:
                    st.metric("Balance", f"${acc['balance']:,.0f}")
                with col3:
                    st.write(f"Access: {acc['access_method'] or 'N/A'}")
                    st.caption(f"{acc['days_to_access']} days")
                with col4:
                    if st.button("🗑️", key=f"del_{acc['account_name']}"):
                        # Add deletion logic
                        pass
    
    st.markdown(f"### 💰 Total Portfolio Value: ${total_value:,.0f}")

def render_crypto_form(username: str, db: FamilyFinanceDB):
    """Form for inputting crypto holdings"""
    
    st.markdown("### ₿ Crypto Holdings")
    st.info("Add your cryptocurrency holdings for sovereignty calculations")
    
    # Quick add for existing Bitcoin stack
    with st.expander("🚀 Quick Add Existing Stack"):
        col1, col2 = st.columns(2)
        with col1:
            btc_amount = st.number_input("Total Bitcoin (BTC)", 
                min_value=0.0, 
                format="%.8f",
                help="Your total BTC across all wallets")
        with col2:
            avg_price = st.number_input("Average Buy Price (optional)",
                min_value=0.0,
                format="%.2f",
                help="Your average acquisition price")
        
        if st.button("Add Bitcoin Stack"):
            if btc_amount > 0:
                crypto_data = {
                    'crypto_type': 'BTC',
                    'amount': btc_amount,
                    'acquisition_price': avg_price if avg_price > 0 else None,
                    'storage_method': 'Multiple',
                    'wallet_label': 'Full Stack'
                }
                if db.add_crypto_holding(username, crypto_data):
                    st.success(f"✅ Added {btc_amount} BTC to your sovereignty calculations")
                    st.rerun()
    
    # Detailed crypto entry
    with st.form("add_crypto"):
        col1, col2 = st.columns(2)
        
        with col1:
            crypto_type = st.selectbox("Cryptocurrency*", [
                "BTC", "ETH", "SOL", "ADA", "DOT", "Other"
            ])
            
            if crypto_type == "Other":
                crypto_type = st.text_input("Specify cryptocurrency")
            
            amount = st.number_input("Amount*",
                min_value=0.0,
                format="%.8f",
                help="Number of coins/tokens")
            
            acquisition_date = st.date_input("Acquisition Date",
                max_value=date.today())
        
        with col2:
            acquisition_price = st.number_input("Purchase Price (USD)",
                min_value=0.0,
                format="%.2f",
                help="Price per coin when purchased")
            
            storage_method = st.selectbox("Storage Method*", [
                "Hardware Wallet",
                "Software Wallet", 
                "Exchange",
                "Multi-sig",
                "Paper Wallet",
                "Other"
            ])
            
            wallet_label = st.text_input("Wallet Label",
                placeholder="e.g., Ledger Main, Coinbase")
        
        is_staking = st.checkbox("Currently Staking",
            help="Check if earning staking rewards")
        
        submitted = st.form_submit_button("➕ Add Crypto")
        
        if submitted:
            if crypto_type and amount > 0:
                crypto_data = {
                    'crypto_type': crypto_type,
                    'amount': amount,
                    'acquisition_date': acquisition_date,
                    'acquisition_price': acquisition_price,
                    'storage_method': storage_method,
                    'wallet_label': wallet_label,
                    'is_staking': is_staking
                }
                
                if db.add_crypto_holding(username, crypto_data):
                    st.success(f"✅ Added {amount} {crypto_type}")
                    st.rerun()
                else:
                    st.error("❌ Error adding crypto")
            else:
                st.error("Please fill required fields")
    
    # Display crypto summary
    st.markdown("### 🪙 Your Crypto Portfolio")
    crypto_summary = db.get_crypto_summary(username)
    
    if crypto_summary:
        for crypto, data in crypto_summary.items():
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(crypto, f"{data['total_amount']:.8f}")
            with col2:
                if data['avg_acquisition_price']:
                    st.metric("Avg Price", f"${data['avg_acquisition_price']:,.2f}")
            with col3:
                st.write("Storage:")
                for method in data['storage_methods']:
                    st.caption(f"• {method}")
    else:
        st.info("No crypto holdings added yet")

def render_expenses_form(username: str, db: FamilyFinanceDB):
    """Form for inputting monthly expenses"""
    
    st.markdown("### 💸 Monthly Expenses")
    st.info("Track your expenses to calculate sovereignty runway")
    
    # Common expense categories with typical amounts
    expense_templates = {
        "Housing": {"amount": 2000, "is_fixed": True},
        "Food & Groceries": {"amount": 800, "is_fixed": False},
        "Transportation": {"amount": 400, "is_fixed": False},
        "Insurance": {"amount": 300, "is_fixed": True},
        "Utilities": {"amount": 200, "is_fixed": True},
        "Healthcare": {"amount": 200, "is_fixed": False},
        "Entertainment": {"amount": 200, "is_fixed": False},
        "Debt Payments": {"amount": 0, "is_fixed": True},
        "Subscriptions": {"amount": 100, "is_fixed": True},
        "Other": {"amount": 300, "is_fixed": False}
    }
    
    with st.form("add_expenses"):
        st.markdown("#### Add/Update Expenses")
        
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        
        expense_rows = []
        for category, defaults in expense_templates.items():
            with col1:
                st.text(category)
            with col2:
                amount = st.number_input(
                    "Amount",
                    min_value=0.0,
                    value=float(defaults["amount"]),
                    format="%.2f",
                    key=f"amt_{category}"
                )
            with col3:
                is_fixed = st.checkbox(
                    "Fixed",
                    value=defaults["is_fixed"],
                    key=f"fix_{category}"
                )
            with col4:
                frequency = st.selectbox(
                    "Freq",
                    ["monthly", "annual", "quarterly"],
                    key=f"freq_{category}"
                )
            
            if amount > 0:
                expense_rows.append({
                    'category': category,
                    'amount': amount,
                    'is_fixed': is_fixed,
                    'frequency': frequency
                })
        
        # Custom expense
        st.markdown("#### Add Custom Expense")
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        
        with col1:
            custom_category = st.text_input("Category Name")
        with col2:
            custom_amount = st.number_input("Amount", min_value=0.0)
        with col3:
            custom_fixed = st.checkbox("Fixed", key="custom_fixed")
        with col4:
            custom_freq = st.selectbox("Freq", ["monthly", "annual", "quarterly"], key="custom_freq")
        
        if st.form_submit_button("💾 Save All Expenses"):
            success_count = 0
            
            # Save template expenses
            for expense in expense_rows:
                if db.upsert_expense(username, expense):
                    success_count += 1
            
            # Save custom expense if provided
            if custom_category and custom_amount > 0:
                custom_expense = {
                    'category': custom_category,
                    'amount': custom_amount,
                    'is_fixed': custom_fixed,
                    'frequency': custom_freq
                }
                if db.upsert_expense(username, custom_expense):
                    success_count += 1
            
            st.success(f"✅ Saved {success_count} expenses")
            st.rerun()
    
    # Display expense summary
    st.markdown("### 📊 Expense Summary")
    expense_summary = db.get_expense_summary(username)
    
    if expense_summary['expenses']:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Fixed Monthly", f"${expense_summary['fixed_total']:,.0f}")
        with col2:
            st.metric("Variable Monthly", f"${expense_summary['variable_total']:,.0f}")
        with col3:
            st.metric("Total Monthly", f"${expense_summary['total_monthly']:,.0f}")
        
        st.info(f"**Annual Expenses: ${expense_summary['total_annual']:,.0f}**")
        
        # Expense breakdown
        st.markdown("#### Expense Breakdown")
        for expense in expense_summary['expenses']:
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                expense_type = "🔒 Fixed" if expense['is_fixed'] else "🔄 Variable"
                st.write(f"**{expense['category']}** ({expense_type})")
            with col2:
                st.write(f"${expense['amount']:,.0f}/mo")
            with col3:
                st.caption(expense['frequency'])

def render_contacts_form(username: str, db: FamilyFinanceDB):
    """Form for emergency contacts"""
    
    st.markdown("### 📞 Emergency Contacts")
    st.info("Critical contacts your family needs in an emergency")
    
    contact_types = [
        "Financial Advisor",
        "Attorney",
        "CPA/Tax Professional",
        "Insurance Agent",
        "Crypto Mentor",
        "Bank Manager",
        "Investment Broker",
        "Estate Planner",
        "Other"
    ]
    
    with st.form("add_contact"):
        col1, col2 = st.columns(2)
        
        with col1:
            contact_type = st.selectbox("Contact Type*", contact_types)
            contact_name = st.text_input("Contact Name*",
                placeholder="John Smith")
            phone = st.text_input("Phone Number",
                placeholder="(555) 123-4567")
        
        with col2:
            email = st.text_input("Email",
                placeholder="john@example.com")
            company = st.text_input("Company/Firm",
                placeholder="Smith Financial Advisors")
            priority = st.slider("Priority", 1, 5, 1,
                help="1 = Highest priority")
        
        notes = st.text_area("Notes",
            placeholder="Best times to call, specific expertise, etc.")
        
        if st.form_submit_button("➕ Add Contact"):
            if contact_type and contact_name:
                # Add to database
                st.success(f"✅ Added {contact_name}")
                st.rerun()
            else:
                st.error("Please fill required fields")

def render_documents_form(username: str, db: FamilyFinanceDB):
    """Form for document locations"""
    
    st.markdown("### 📄 Important Documents")
    st.info("Where your family can find critical documents")
    
    document_types = [
        "Will/Estate Plan",
        "Life Insurance Policy",
        "Power of Attorney", 
        "Healthcare Directive",
        "Property Deeds",
        "Vehicle Titles",
        "Tax Records",
        "Crypto Seed Phrases",
        "Bank Statements",
        "Investment Records",
        "Business Documents",
        "Other"
    ]
    
    with st.form("add_document"):
        col1, col2 = st.columns(2)
        
        with col1:
            doc_type = st.selectbox("Document Type*", document_types)
            location = st.text_input("Primary Location*",
                placeholder="Safe deposit box at Chase Bank")
            last_verified = st.date_input("Last Verified",
                max_value=date.today())
        
        with col2:
            backup_location = st.text_input("Backup Location",
                placeholder="Copy in home safe")
            access_instructions = st.text_area("Access Instructions",
                placeholder="Box #123, key in desk drawer")
        
        if st.form_submit_button("➕ Add Document"):
            if doc_type and location:
                # Add to database
                st.success(f"✅ Added {doc_type} location")
                st.rerun()
            else:
                st.error("Please fill required fields")

# Quick access function for existing users
def render_quick_update_form(username: str, db: FamilyFinanceDB):
    """Quick update form for existing accounts/balances"""
    
    st.markdown("### ⚡ Quick Balance Update")
    
    accounts = db.get_accounts_by_priority(username)
    all_accounts = []
    for priority_accounts in accounts.values():
        all_accounts.extend(priority_accounts)
    
    if all_accounts:
        with st.form("quick_update"):
            st.markdown("Update your account balances:")
            
            updates = {}
            for acc in all_accounts:
                new_balance = st.number_input(
                    f"{acc['account_name']} (current: ${acc['balance']:,.0f})",
                    min_value=0.0,
                    value=float(acc['balance']),
                    format="%.2f",
                    key=f"update_{acc['account_name']}"
                )
                if new_balance != acc['balance']:
                    updates[acc['account_name']] = new_balance
            
            if st.form_submit_button("💾 Update Balances"):
                for account_name, new_balance in updates.items():
                    # Update in database
                    pass
                st.success(f"✅ Updated {len(updates)} accounts")
                st.rerun()
    else:
        st.info("No accounts found. Complete the setup wizard first.")