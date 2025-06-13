# migrate_existing_data.py
"""
Helper script to migrate existing user data into the new database schema
Handles both manual entry and CSV import options
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from family_finance_database import FamilyFinanceDB
from db import get_db_connection  # Add this import

def render_migration_wizard(username: str):
    """Data migration wizard for existing users"""
    
    st.markdown("""
    ### 🔄 Import Your Existing Financial Data
    
    Choose how you'd like to import your data:
    """)
    
    import_method = st.radio("Import Method", [
        "Quick Manual Entry",
        "CSV Upload", 
        "Copy from Another User",
        "Start Fresh"
    ])
    
    db = FamilyFinanceDB()
    
    if import_method == "Quick Manual Entry":
        render_quick_import(username, db)
    elif import_method == "CSV Upload":
        render_csv_import(username, db)
    elif import_method == "Copy from Another User":
        render_copy_from_user(username, db)
    else:
        st.info("Use the setup wizard to enter your data step by step")

def render_quick_import(username: str, db: FamilyFinanceDB):
    """Quick import for users who know their totals"""
    
    st.markdown("### 💨 Quick Import - Enter Your Totals")
    
    with st.form("quick_import"):
        st.markdown("#### Financial Accounts")
        col1, col2 = st.columns(2)
        
        with col1:
            # Immediate access
            checking = st.number_input("Checking Account(s) Total", min_value=0.0)
            savings = st.number_input("Savings Account(s) Total", min_value=0.0)
            cash = st.number_input("Cash/Emergency Fund", min_value=0.0)
            
            # Investment accounts
            investment = st.number_input("Investment Accounts Total", min_value=0.0)
            retirement_401k = st.number_input("401k/403b Total", min_value=0.0)
            ira = st.number_input("IRA Accounts Total", min_value=0.0)
        
        with col2:
            # Crypto
            btc_amount = st.number_input("Bitcoin (BTC)", min_value=0.0, format="%.8f")
            btc_avg_price = st.number_input("BTC Average Buy Price", min_value=0.0)
            other_crypto_value = st.number_input("Other Crypto (USD value)", min_value=0.0)
            
            # Real estate and other
            home_equity = st.number_input("Home Equity", min_value=0.0)
            other_assets = st.number_input("Other Assets", min_value=0.0)
        
        st.markdown("#### Monthly Expenses")
        col1, col2 = st.columns(2)
        
        with col1:
            housing = st.number_input("Housing (rent/mortgage)", min_value=0.0)
            food = st.number_input("Food & Groceries", min_value=0.0)
            transport = st.number_input("Transportation", min_value=0.0)
            insurance = st.number_input("Insurance (all types)", min_value=0.0)
        
        with col2:
            utilities = st.number_input("Utilities", min_value=0.0)
            healthcare = st.number_input("Healthcare", min_value=0.0)
            other_expenses = st.number_input("All Other Expenses", min_value=0.0)
        
        if st.form_submit_button("🚀 Import All Data"):
            success_count = 0
            
            # Import accounts
            account_imports = [
                ("Checking Accounts", "Checking", checking, "immediate"),
                ("Savings Accounts", "Savings", savings, "immediate"),
                ("Cash/Emergency Fund", "Savings", cash, "immediate"),
                ("Investment Accounts", "Investment", investment, "short_term"),
                ("401k/403b", "Retirement (401k)", retirement_401k, "long_term"),
                ("IRA Accounts", "Retirement (IRA)", ira, "long_term"),
                ("Home Equity", "Real Estate", home_equity, "long_term"),
                ("Other Assets", "Other", other_assets, "medium_term")
            ]
            
            for name, acc_type, balance, priority in account_imports:
                if balance > 0:
                    account_data = {
                        'account_name': name,
                        'account_type': acc_type,
                        'balance': balance,
                        'access_priority': priority,
                        'institution': 'Multiple' if 'Accounts' in name else ''
                    }
                    if db.upsert_account(username, account_data):
                        success_count += 1
            
            # Import Bitcoin
            if btc_amount > 0:
                crypto_data = {
                    'crypto_type': 'BTC',
                    'amount': btc_amount,
                    'acquisition_price': btc_avg_price if btc_avg_price > 0 else None,
                    'storage_method': 'Multiple',
                    'wallet_label': 'Imported Stack'
                }
                if db.add_crypto_holding(username, crypto_data):
                    success_count += 1
            
            # Import expenses
            expense_imports = [
                ("Housing", housing, True),
                ("Food & Groceries", food, False),
                ("Transportation", transport, False),
                ("Insurance", insurance, True),
                ("Utilities", utilities, True),
                ("Healthcare", healthcare, False),
                ("Other Expenses", other_expenses, False)
            ]
            
            for category, amount, is_fixed in expense_imports:
                if amount > 0:
                    expense_data = {
                        'category': category,
                        'amount': amount,
                        'is_fixed': is_fixed,
                        'frequency': 'monthly'
                    }
                    if db.upsert_expense(username, expense_data):
                        success_count += 1
            
            st.success(f"✅ Successfully imported {success_count} items!")
            st.balloons()
            
            # Calculate and show sovereignty status
            btc_price = 50000  # You'd get this from your price API
            metrics = db.calculate_sovereignty_metrics(username, btc_price)
            
            st.markdown(f"""
            ### 🎉 Your Sovereignty Status: {metrics['sovereignty_status']}
            
            - **Sovereignty Ratio:** {metrics['sovereignty_ratio']:.2f} years
            - **Emergency Runway:** {metrics['emergency_runway_months']:.1f} months
            - **Total Portfolio:** ${metrics['total_assets']:,.0f}
            """)

def render_csv_import(username: str, db: FamilyFinanceDB):
    """CSV import for detailed data"""
    
    st.markdown("### 📁 CSV Import")
    
    # Download templates
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Download Accounts Template"):
            template_df = pd.DataFrame({
                'account_name': ['Chase Checking', 'Vanguard Brokerage'],
                'account_type': ['Checking', 'Investment'],
                'institution': ['Chase Bank', 'Vanguard'],
                'balance': [5000, 50000],
                'access_priority': ['immediate', 'short_term'],
                'access_method': ['Online banking', 'Phone + online'],
                'days_to_access': [0, 3],
                'is_joint': [True, False]
            })
            csv = template_df.to_csv(index=False)
            st.download_button(
                "Download",
                csv,
                "accounts_template.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📥 Download Crypto Template"):
            template_df = pd.DataFrame({
                'crypto_type': ['BTC', 'ETH'],
                'amount': [0.5, 10.0],
                'acquisition_date': ['2021-01-15', '2021-06-30'],
                'acquisition_price': [35000, 2000],
                'storage_method': ['Hardware Wallet', 'Exchange'],
                'wallet_label': ['Ledger Main', 'Coinbase']
            })
            csv = template_df.to_csv(index=False)
            st.download_button(
                "Download", 
                csv,
                "crypto_template.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("📥 Download Expenses Template"):
            template_df = pd.DataFrame({
                'expense_category': ['Housing', 'Food & Groceries', 'Transportation'],
                'amount': [2000, 800, 400],
                'is_fixed': [True, False, False],
                'frequency': ['monthly', 'monthly', 'monthly']
            })
            csv = template_df.to_csv(index=False)
            st.download_button(
                "Download",
                csv,
                "expenses_template.csv",
                mime="text/csv"
            )
    
    st.markdown("---")
    
    # File uploaders
    accounts_file = st.file_uploader("Upload Accounts CSV", type=['csv'])
    if accounts_file:
        try:
            df = pd.read_csv(accounts_file)
            st.write(f"Found {len(df)} accounts to import")
            
            if st.button("Import Accounts"):
                success = 0
                for _, row in df.iterrows():
                    account_data = row.to_dict()
                    if db.upsert_account(username, account_data):
                        success += 1
                st.success(f"✅ Imported {success} accounts")
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
    
    crypto_file = st.file_uploader("Upload Crypto CSV", type=['csv'])
    if crypto_file:
        try:
            df = pd.read_csv(crypto_file)
            st.write(f"Found {len(df)} crypto entries to import")
            
            if st.button("Import Crypto"):
                success = 0
                for _, row in df.iterrows():
                    crypto_data = row.to_dict()
                    if db.add_crypto_holding(username, crypto_data):
                        success += 1
                st.success(f"✅ Imported {success} crypto holdings")
        except Exception as e:
            st.error(f"Error reading CSV: {e}")

def render_copy_from_user(username: str, db: FamilyFinanceDB):
    """Copy data from another user (e.g., spouse)"""
    
    st.markdown("### 👥 Copy from Another User")
    st.info("This is useful for copying a spouse's setup or using a template account")
    
    source_user = st.text_input("Source Username", 
        placeholder="Enter username to copy from")
    
    if source_user:
        # Check if source exists
        source_accounts = db.get_accounts_by_priority(source_user)
        has_data = any(source_accounts[p] for p in source_accounts)
        
        if has_data:
            st.success(f"✅ Found data for {source_user}")
            
            # Show what will be copied
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Will Copy:**")
                st.write("• Account structure")
                st.write("• Expense categories")
                st.write("• Document types")
                st.write("• Contact types")
            
            with col2:
                st.markdown("**Won't Copy:**")
                st.write("• Account balances")
                st.write("• Actual amounts")
                st.write("• Personal details")
                st.write("• Crypto holdings")
            
            if st.button("Copy Structure", type="primary"):
                # Copy account structure
                for priority, accounts in source_accounts.items():
                    for acc in accounts:
                        new_acc = acc.copy()
                        new_acc['balance'] = 0  # Reset balance
                        new_acc['notes'] = f"Copied from {source_user}"
                        db.upsert_account(username, new_acc)
                
                # Copy expense structure
                source_expenses = db.get_expense_summary(source_user)
                for exp in source_expenses['expenses']:
                    new_exp = {
                        'category': exp['category'],
                        'amount': 0,  # Reset amount
                        'is_fixed': exp['is_fixed'],
                        'frequency': exp['frequency']
                    }
                    db.upsert_expense(username, new_exp)
                
                st.success("✅ Successfully copied structure! Now update with your actual values.")
        else:
            st.error(f"No data found for user: {source_user}")

# Bulk operations helper
def render_bulk_operations(username: str, db: FamilyFinanceDB):
    """Bulk operations for power users"""
    
    st.markdown("### ⚡ Bulk Operations")
    
    operation = st.selectbox("Operation", [
        "Update All Account Balances",
        "Adjust All Expenses by %",
        "Mark Accounts as Joint",
        "Export All Data"
    ])
    
    if operation == "Update All Account Balances":
        multiplier = st.slider("Adjust all balances by", 0.5, 2.0, 1.0, 0.05)
        
        if st.button(f"Apply {multiplier}x to All Balances"):
            accounts = db.get_accounts_by_priority(username)
            updated = 0
            
            for priority_accounts in accounts.values():
                for acc in priority_accounts:
                    acc['balance'] = acc['balance'] * multiplier
                    if db.upsert_account(username, acc):
                        updated += 1
            
            st.success(f"✅ Updated {updated} accounts")
    
    elif operation == "Export All Data":
        if st.button("Generate Export"):
            # Create comprehensive export
            export_data = {
                'export_date': datetime.now().isoformat(),
                'username': username,
                'accounts': db.get_accounts_by_priority(username),
                'crypto': db.get_crypto_summary(username),
                'expenses': db.get_expense_summary(username),
                'metrics': db.calculate_sovereignty_metrics(username, 50000)
            }
            
            json_str = json.dumps(export_data, indent=2)
            st.download_button(
                "📥 Download Full Export",
                json_str,
                f"sovereignty_export_{username}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )

# Integration helpers
def estimate_from_habits(username: str) -> dict:
    """Estimate financial data from existing habit tracking"""
    
    conn = get_db_connection()
    
    # Get spending habits
    no_spending_days = conn.execute("""
        SELECT COUNT(*) FROM daily_scores 
        WHERE username = ? AND no_spending = 1
        AND timestamp > datetime('now', '-90 days')
    """, [username]).fetchone()[0]
    
    # Get investment habits
    btc_investments = conn.execute("""
        SELECT SUM(invested_bitcoin) FROM daily_scores
        WHERE username = ? AND invested_bitcoin > 0
    """, [username]).fetchone()[0] or 0
    
    # Rough estimates based on habits
    estimates = {
        'monthly_spending': 3000 * (1 - no_spending_days/90),  # Rough estimate
        'btc_invested_usd': btc_investments,
        'suggested_emergency': 10000,  # Default suggestion
        'estimated_income': 5000  # Default estimate
    }
    
    return estimates