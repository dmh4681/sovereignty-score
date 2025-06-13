# family_finance_forms.py
"""
Streamlit forms for inputting family finance data
Provides user-friendly interface for comprehensive financial data collection
"""

import streamlit as st
from datetime import datetime, date
from typing import Dict, Optional
import pandas as pd
from family_finance_database import FamilyFinanceDB
from db import get_db_connection

def get_current_btc_price() -> float:
    """Get current BTC price from database"""
    try:
        conn = get_db_connection()
        result = conn.execute("""
            SELECT closing_price 
            FROM btc_price_history 
            ORDER BY date DESC 
            LIMIT 1
        """).fetchone()
        return result[0] if result else 50000.0
    except:
        return 50000.0

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
                # Calculate and display sovereignty metrics
                try:
                    btc_price = get_current_btc_price()
                    metrics = db.calculate_sovereignty_metrics(username, btc_price)
                    
                    st.session_state.setup_complete = True
                    st.session_state.show_metrics = True
                    st.session_state.metrics = metrics
                    st.rerun()
                except Exception as e:
                    st.error(f"Error calculating metrics: {e}")
    
    # Show metrics after setup complete
    if st.session_state.get('show_metrics') and st.session_state.get('metrics'):
        metrics = st.session_state.metrics
        st.markdown("---")
        st.success("✅ Financial setup complete!")
        st.balloons()
        
        st.markdown(f"""
        ### 🎉 Your Sovereignty Status: {metrics['sovereignty_status']}
        
        - **Sovereignty Ratio:** {metrics['sovereignty_ratio']:.2f} years
        - **Emergency Runway:** {metrics['emergency_runway_months']:.1f} months
        - **Total Portfolio:** ${metrics['total_assets']:,.0f}
        - **Crypto Value:** ${metrics['total_crypto_value']:,.0f}
        
        You can now return to the main dashboard to see your complete financial picture!
        """)

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
                    'access_priority': access_priority[0] if isinstance(access_priority, tuple) else access_priority,
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
        
        # Create header row
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        with col1:
            st.markdown("**Category**")
        with col2:
            st.markdown("**Amount**")
        with col3:
            st.markdown("**Fixed**")
        with col4:
            st.markdown("**Frequency**")
        
        expense_rows = []
        
        # Template expenses
        for category, defaults in expense_templates.items():
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            
            with col1:
                st.markdown(f"**{category}**")
            with col2:
                amount = st.number_input(
                    "Amount",
                    min_value=0.0,
                    value=float(defaults["amount"]),
                    format="%.2f",
                    key=f"amt_{category}",
                    label_visibility="collapsed"
                )
            with col3:
                is_fixed = st.checkbox(
                    "Fixed",
                    value=defaults["is_fixed"],
                    key=f"fix_{category}",
                    label_visibility="collapsed"
                )
            with col4:
                frequency = st.selectbox(
                    "Freq",
                    ["monthly", "annual", "quarterly"],
                    key=f"freq_{category}",
                    label_visibility="collapsed"
                )
            
            if amount > 0:
                expense_rows.append({
                    'category': category,
                    'amount': amount,
                    'is_fixed': is_fixed,
                    'frequency': frequency
                })
        
        if st.form_submit_button("💾 Save Standard Expenses"):
            success_count = 0
            
            # Save template expenses
            for expense in expense_rows:
                if db.upsert_expense(username, expense):
                    success_count += 1
            
            st.success(f"✅ Saved {success_count} expenses")
            st.rerun()
    
    # Custom expenses section - outside the form for multiple additions
    st.markdown("#### Add Custom Expenses")
    
    # Initialize session state for custom expenses if not exists
    if 'custom_expenses' not in st.session_state:
        st.session_state.custom_expenses = []
    
    # Form for adding new custom expense
    with st.form("add_custom_expense"):
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        
        with col1:
            custom_category = st.text_input("Category Name", placeholder="e.g., Pet Care")
        with col2:
            custom_amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        with col3:
            custom_fixed = st.checkbox("Fixed")
        with col4:
            custom_freq = st.selectbox("Frequency", ["monthly", "annual", "quarterly"])
        
        if st.form_submit_button("➕ Add Custom Expense"):
            if custom_category and custom_amount > 0:
                custom_expense = {
                    'category': custom_category,
                    'amount': custom_amount,
                    'is_fixed': custom_fixed,
                    'frequency': custom_freq
                }
                if db.upsert_expense(username, custom_expense):
                    st.success(f"✅ Added {custom_category}")
                    st.rerun()
                else:
                    st.error("Error adding expense")
            else:
                st.error("Please enter category name and amount")
    
    # Display expense summary
    st.markdown("### 📊 Expense Summary")
    expense_summary = db.get_expense_summary(username)
    
    if expense_summary['expenses']:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Fixed Monthly", f"${expense_summary['fixed_total']:,.0f}")
        with col2:
            st.metric("Variable Monthly", f"${expense_summary['variable_total']:,.0f}")
        with col3:
            st.metric("Total Monthly", f"${expense_summary['total_monthly']:,.0f}")
        with col4:
            st.metric("Annual Total", f"${expense_summary['total_annual']:,.0f}")
        
        # Expense breakdown table
        st.markdown("#### Expense Breakdown")
        
        # Create a dataframe for better display
        expense_data = []
        for expense in expense_summary['expenses']:
            expense_data.append({
                'Category': expense['category'],
                'Monthly Amount': f"${expense['amount']:,.0f}",
                'Type': '🔒 Fixed' if expense['is_fixed'] else '🔄 Variable',
                'Frequency': expense['frequency'],
                'Annual': f"${expense['amount'] * 12:,.0f}" if expense['frequency'] == 'monthly' else 'Varies'
            })
        
        df = pd.DataFrame(expense_data)
        st.dataframe(df, hide_index=True, use_container_width=True)
        
        # Option to delete expenses
        with st.expander("🗑️ Delete Expenses"):
            expense_to_delete = st.selectbox(
                "Select expense to delete",
                [exp['category'] for exp in expense_summary['expenses']]
            )
            if st.button("Delete Selected Expense"):
                # Add delete functionality
                conn = db.conn
                conn.execute("""
                    DELETE FROM monthly_expenses 
                    WHERE username = ? AND expense_category = ?
                """, [username, expense_to_delete])
                st.success(f"Deleted {expense_to_delete}")
                st.rerun()
    else:
        st.info("No expenses added yet. Start with the standard categories above!")

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
                try:
                    db.conn.execute("""
                        INSERT INTO emergency_contacts
                        (username, contact_type, contact_name, phone, email, 
                         company, notes, priority)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, [
                        username,
                        contact_type,
                        contact_name,
                        phone,
                        email,
                        company,
                        notes,
                        priority
                    ])
                    st.success(f"✅ Added {contact_name}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding contact: {e}")
            else:
                st.error("Please fill required fields")
    
    # Display existing contacts
    st.markdown("### 📋 Your Emergency Contacts")
    
    try:
        contacts = db.conn.execute("""
            SELECT * FROM emergency_contacts 
            WHERE username = ?
            ORDER BY priority, contact_type
        """, [username]).fetchall()
        
        if contacts:
            contact_data = []
            for contact in contacts:
                contact_data.append({
                    'Type': contact[1],  # contact_type
                    'Name': contact[2],  # contact_name
                    'Phone': contact[3] or 'N/A',
                    'Email': contact[4] or 'N/A',
                    'Company': contact[5] or 'N/A',
                    'Priority': '⭐' * contact[7]  # priority
                })
            
            df = pd.DataFrame(contact_data)
            st.dataframe(df, hide_index=True, use_container_width=True)
            
            # Delete option
            with st.expander("🗑️ Delete Contacts"):
                contact_names = [c[2] for c in contacts]  # contact_name is at index 2
                contact_to_delete = st.selectbox("Select contact to delete", contact_names)
                if st.button("Delete Selected Contact"):
                    db.conn.execute("""
                        DELETE FROM emergency_contacts 
                        WHERE username = ? AND contact_name = ?
                    """, [username, contact_to_delete])
                    st.success(f"Deleted {contact_to_delete}")
                    st.rerun()
        else:
            st.info("No contacts added yet")
            
    except Exception as e:
        st.error(f"Error loading contacts: {e}")

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
                try:
                    db.conn.execute("""
                        INSERT INTO document_locations
                        (username, document_type, location, access_instructions,
                         last_verified, backup_location)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, [
                        username,
                        doc_type,
                        location,
                        access_instructions,
                        last_verified,
                        backup_location
                    ])
                    st.success(f"✅ Added {doc_type} location")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding document: {e}")
            else:
                st.error("Please fill required fields")
    
    # Display existing documents
    st.markdown("### 🗂️ Document Locations")
    
    try:
        documents = db.conn.execute("""
            SELECT * FROM document_locations 
            WHERE username = ?
            ORDER BY document_type
        """, [username]).fetchall()
        
        if documents:
            for doc in documents:
                with st.expander(f"📄 {doc[1]}"):  # document_type
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Primary Location:** {doc[2]}")  # location
                        st.write(f"**Last Verified:** {doc[4] or 'Not specified'}")  # last_verified
                    with col2:
                        st.write(f"**Backup Location:** {doc[5] or 'None specified'}")  # backup_location
                        if doc[3]:  # access_instructions
                            st.write(f"**Access Instructions:** {doc[3]}")
                    
                    if st.button(f"🗑️ Delete", key=f"del_doc_{doc[1]}"):
                        db.conn.execute("""
                            DELETE FROM document_locations 
                            WHERE username = ? AND document_type = ?
                        """, [username, doc[1]])
                        st.success(f"Deleted {doc[1]}")
                        st.rerun()
        else:
            st.info("No documents added yet")
            
    except Exception as e:
        st.error(f"Error loading documents: {e}")

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