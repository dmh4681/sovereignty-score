# family_finance_database.py
"""
Database schema and management for Family Finance Plan
Enables proper input, storage, and retrieval of all financial data
"""

import duckdb
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class FamilyFinanceDB:
    """Manages all family finance data persistence"""
    
    def __init__(self, db_path: str = "sovereignty_tracker.db"):
        self.conn = duckdb.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        """Create all necessary tables for family finance tracking"""
        
        # Financial accounts table - stores all account details
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS financial_accounts (
                username TEXT NOT NULL,
                account_name TEXT NOT NULL,
                account_type TEXT NOT NULL, -- checking, savings, investment, crypto, retirement, etc.
                institution TEXT,
                balance REAL DEFAULT 0,
                currency TEXT DEFAULT 'USD',
                access_priority TEXT, -- immediate, short_term, medium_term, long_term
                access_method TEXT, -- online, bank_visit, hardware_wallet, etc.
                days_to_access INTEGER DEFAULT 0,
                is_joint BOOLEAN DEFAULT FALSE,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                PRIMARY KEY (username, account_name)
            )
        """)
        
        # Crypto holdings - separate table for detailed crypto tracking
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS crypto_holdings (
                username TEXT NOT NULL,
                crypto_type TEXT NOT NULL, -- BTC, ETH, etc.
                amount REAL NOT NULL,
                acquisition_date DATE,
                acquisition_price REAL,
                storage_method TEXT, -- hardware_wallet, exchange, etc.
                wallet_label TEXT,
                is_staking BOOLEAN DEFAULT FALSE,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (username, crypto_type, wallet_label)
            )
        """)
        
        # Monthly expenses tracking
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS monthly_expenses (
                username TEXT NOT NULL,
                expense_category TEXT NOT NULL, -- housing, food, transport, etc.
                amount REAL NOT NULL,
                is_fixed BOOLEAN DEFAULT TRUE,
                frequency TEXT DEFAULT 'monthly', -- monthly, annual, quarterly
                notes TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (username, expense_category)
            )
        """)
        
        # Emergency contacts
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS emergency_contacts (
                username TEXT NOT NULL,
                contact_type TEXT NOT NULL, -- financial_advisor, attorney, crypto_mentor, etc.
                contact_name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                company TEXT,
                notes TEXT,
                priority INTEGER DEFAULT 1,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (username, contact_name)
            )
        """)
        
        # Document locations
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS document_locations (
                username TEXT NOT NULL,
                document_type TEXT NOT NULL, -- will, insurance, seed_phrase, etc.
                location TEXT NOT NULL,
                access_instructions TEXT,
                last_verified DATE,
                backup_location TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (username, document_type)
            )
        """)
        
        # Family training progress
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS family_training (
                username TEXT NOT NULL,
                training_topic TEXT NOT NULL,
                family_member TEXT,
                completion_date DATE,
                comfort_level INTEGER CHECK (comfort_level >= 1 AND comfort_level <= 10),
                notes TEXT,
                next_review_date DATE,
                PRIMARY KEY (username, training_topic, family_member)
            )
        """)
        
        # Sovereignty calculations snapshot
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sovereignty_snapshot (
                username TEXT NOT NULL,
                snapshot_date DATE DEFAULT CURRENT_DATE,
                total_assets REAL,
                total_crypto REAL,
                total_traditional REAL,
                monthly_expenses REAL,
                annual_expenses REAL,
                sovereignty_ratio REAL,
                full_sovereignty_ratio REAL,
                sovereignty_status TEXT,
                emergency_runway_months REAL,
                btc_price_at_snapshot REAL,
                notes TEXT,
                PRIMARY KEY (username, snapshot_date)
            )
        """)
    
    # Account Management Methods
    def upsert_account(self, username: str, account_data: Dict) -> bool:
        """Insert or update financial account"""
        try:
            # Check if account exists
            existing = self.conn.execute("""
                SELECT account_name FROM financial_accounts 
                WHERE username = ? AND account_name = ?
            """, [username, account_data['account_name']]).fetchone()
            
            if existing:
                # Update existing account
                self.conn.execute("""
                    UPDATE financial_accounts 
                    SET account_type = ?,
                        institution = ?,
                        balance = ?,
                        currency = ?,
                        access_priority = ?,
                        access_method = ?,
                        days_to_access = ?,
                        is_joint = ?,
                        notes = ?,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE username = ? AND account_name = ?
                """, [
                    account_data['account_type'],
                    account_data.get('institution', ''),
                    account_data['balance'],
                    account_data.get('currency', 'USD'),
                    account_data['access_priority'],
                    account_data.get('access_method', ''),
                    account_data.get('days_to_access', 0),
                    account_data.get('is_joint', False),
                    account_data.get('notes', ''),
                    username,
                    account_data['account_name']
                ])
            else:
                # Insert new account
                self.conn.execute("""
                    INSERT INTO financial_accounts 
                    (username, account_name, account_type, institution, balance, 
                     currency, access_priority, access_method, days_to_access, 
                     is_joint, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    username,
                    account_data['account_name'],
                    account_data['account_type'],
                    account_data.get('institution', ''),
                    account_data['balance'],
                    account_data.get('currency', 'USD'),
                    account_data['access_priority'],
                    account_data.get('access_method', ''),
                    account_data.get('days_to_access', 0),
                    account_data.get('is_joint', False),
                    account_data.get('notes', '')
                ])
            return True
        except Exception as e:
            print(f"Error upserting account: {e}")
            return False
    
    def get_accounts_by_priority(self, username: str) -> Dict[str, List[Dict]]:
        """Get all accounts organized by access priority"""
        result = self.conn.execute("""
            SELECT * FROM financial_accounts 
            WHERE username = ?
            ORDER BY access_priority, balance DESC
        """, [username]).fetchall()
        
        accounts = {
            'immediate': [],
            'short_term': [],
            'medium_term': [],
            'long_term': []
        }
        
        for row in result:
            account = {
                'account_name': row[1],
                'account_type': row[2],
                'institution': row[3],
                'balance': row[4],
                'currency': row[5],
                'access_method': row[7],
                'days_to_access': row[8],
                'is_joint': row[9],
                'notes': row[11]
            }
            priority = row[6]
            if priority in accounts:
                accounts[priority].append(account)
        
        return accounts
    
    # Crypto Management
    def add_crypto_holding(self, username: str, crypto_data: Dict) -> bool:
        """Add crypto holding record"""
        try:
            self.conn.execute("""
                INSERT INTO crypto_holdings
                (username, crypto_type, amount, acquisition_date, 
                 acquisition_price, storage_method, wallet_label, is_staking)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                username,
                crypto_data['crypto_type'],
                crypto_data['amount'],
                crypto_data.get('acquisition_date'),
                crypto_data.get('acquisition_price'),
                crypto_data['storage_method'],
                crypto_data.get('wallet_label', ''),
                crypto_data.get('is_staking', False)
            ])
            return True
        except Exception as e:
            print(f"Error adding crypto: {e}")
            return False
    
    def get_crypto_summary(self, username: str) -> Dict:
        """Get crypto holdings summary"""
        result = self.conn.execute("""
            SELECT 
                crypto_type,
                SUM(amount) as total_amount,
                COUNT(*) as num_transactions,
                AVG(acquisition_price) as avg_price,
                GROUP_CONCAT(DISTINCT storage_method) as storage_methods
            FROM crypto_holdings
            WHERE username = ?
            GROUP BY crypto_type
        """, [username]).fetchall()
        
        summary = {}
        for row in result:
            summary[row[0]] = {
                'total_amount': row[1],
                'num_transactions': row[2],
                'avg_acquisition_price': row[3],
                'storage_methods': row[4].split(',') if row[4] else []
            }
        return summary
    
    # Expense Management
    def upsert_expense(self, username: str, expense_data: Dict) -> bool:
        """Insert or update monthly expense"""
        try:
            # Convert to monthly amount based on frequency
            monthly_amount = expense_data['amount']
            if expense_data.get('frequency') == 'annual':
                monthly_amount = expense_data['amount'] / 12
            elif expense_data.get('frequency') == 'quarterly':
                monthly_amount = expense_data['amount'] / 3
            
            # First check if expense exists
            existing = self.conn.execute("""
                SELECT expense_category FROM monthly_expenses 
                WHERE username = ? AND expense_category = ?
            """, [username, expense_data['category']]).fetchone()
            
            if existing:
                # Update existing
                self.conn.execute("""
                    UPDATE monthly_expenses 
                    SET amount = ?, is_fixed = ?, frequency = ?, notes = ?, 
                        last_updated = CURRENT_TIMESTAMP
                    WHERE username = ? AND expense_category = ?
                """, [
                    monthly_amount,
                    expense_data.get('is_fixed', True),
                    expense_data.get('frequency', 'monthly'),
                    expense_data.get('notes', ''),
                    username,
                    expense_data['category']
                ])
            else:
                # Insert new
                self.conn.execute("""
                    INSERT INTO monthly_expenses
                    (username, expense_category, amount, is_fixed, frequency, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, [
                    username,
                    expense_data['category'],
                    monthly_amount,
                    expense_data.get('is_fixed', True),
                    expense_data.get('frequency', 'monthly'),
                    expense_data.get('notes', '')
                ])
            return True
        except Exception as e:
            print(f"Error upserting expense: {e}")
            return False
    
    def get_expense_summary(self, username: str) -> Dict:
        """Get expense summary with totals"""
        result = self.conn.execute("""
            SELECT 
                expense_category,
                amount,
                is_fixed,
                frequency
            FROM monthly_expenses
            WHERE username = ?
            ORDER BY amount DESC
        """, [username]).fetchall()
        
        fixed_total = 0
        variable_total = 0
        expenses = []
        
        for row in result:
            expense = {
                'category': row[0],
                'amount': row[1],
                'is_fixed': row[2],
                'frequency': row[3]
            }
            expenses.append(expense)
            
            if row[2]:  # is_fixed
                fixed_total += row[1]
            else:
                variable_total += row[1]
        
        return {
            'expenses': expenses,
            'fixed_total': fixed_total,
            'variable_total': variable_total,
            'total_monthly': fixed_total + variable_total,
            'total_annual': (fixed_total + variable_total) * 12
        }
    
    # Sovereignty Calculations
    # family_finance_database.py (updated calculate_sovereignty_metrics method)
    """
    Fixed sovereignty calculation method for FamilyFinanceDB class
    Replace the existing calculate_sovereignty_metrics method with this version
    """

    # family_finance_database.py (updated calculate_sovereignty_metrics method)
    """
    Fixed sovereignty calculation method for FamilyFinanceDB class
    Replace the existing calculate_sovereignty_metrics method with this version
    """

    def calculate_sovereignty_metrics(self, username: str, btc_price: float) -> Dict:
        """Calculate all sovereignty metrics with no hardcoded values"""
        
        # Get account totals by priority
        accounts = self.get_accounts_by_priority(username)
        
        # Calculate total assets from all accounts
        total_assets = 0
        immediate_access = 0
        
        for priority, account_list in accounts.items():
            for acc in account_list:
                total_assets += acc['balance']
                if priority == 'immediate':
                    immediate_access += acc['balance']
        
        # Get crypto holdings and calculate value
        crypto_summary = self.get_crypto_summary(username)
        total_crypto_value = 0
        
        for crypto_type, crypto_data in crypto_summary.items():
            if isinstance(crypto_data, dict) and 'total_amount' in crypto_data:
                # For now, only calculate BTC value. You can add other crypto prices later
                if crypto_type == 'BTC':
                    crypto_value = crypto_data['total_amount'] * btc_price
                    total_crypto_value += crypto_value
                # Add other crypto calculations here as needed
        
        # Add crypto value to total assets
        total_assets += total_crypto_value
        
        # Get expense data
        expense_summary = self.get_expense_summary(username)
        monthly_expenses = expense_summary['total_monthly']
        annual_expenses = expense_summary['total_annual']
        
        # Prevent division by zero
        if monthly_expenses <= 0:
            monthly_expenses = 1
        if annual_expenses <= 0:
            annual_expenses = 12
        
        # Calculate emergency runway (immediate access only)
        emergency_runway_months = immediate_access / monthly_expenses if monthly_expenses > 0 else 0
        
        # Calculate sovereignty ratios
        # Crypto Sovereignty Ratio: crypto value / annual fixed expenses
        fixed_annual = expense_summary['fixed_total'] * 12
        sovereignty_ratio = total_crypto_value / fixed_annual if fixed_annual > 0 else 0
        
        # Full Sovereignty Ratio: total assets / annual total expenses
        full_sovereignty_ratio = total_assets / annual_expenses if annual_expenses > 0 else 0
        
        # Determine sovereignty status based on ratio
        if sovereignty_ratio < 1:
            sovereignty_status = "Vulnerable"
        elif sovereignty_ratio < 3:
            sovereignty_status = "Fragile"
        elif sovereignty_ratio < 6:
            sovereignty_status = "Robust"
        elif sovereignty_ratio < 20:
            sovereignty_status = "Antifragile"
        else:
            sovereignty_status = "Generationally Sovereign"
        
        return {
            'total_assets': total_assets,
            'total_crypto_value': total_crypto_value,
            'monthly_expenses': monthly_expenses,
            'annual_expenses': annual_expenses,
            'emergency_runway_months': emergency_runway_months,
            'sovereignty_ratio': sovereignty_ratio,
            'full_sovereignty_ratio': full_sovereignty_ratio,
            'sovereignty_status': sovereignty_status,
            'immediate_access_total': immediate_access,
            'btc_price': btc_price
        }

    def get_crypto_summary(self, username: str) -> Dict:
        """Get detailed crypto holdings summary with proper aggregation"""
        result = self.conn.execute("""
            SELECT 
                crypto_type,
                SUM(amount) as total_amount,
                AVG(CASE WHEN acquisition_price > 0 THEN acquisition_price ELSE NULL END) as avg_price,
                COUNT(DISTINCT wallet_label) as wallet_count,
                COUNT(DISTINCT storage_method) as storage_method_count,
                MIN(acquisition_date) as first_purchase,
                MAX(acquisition_date) as last_purchase,
                GROUP_CONCAT(DISTINCT storage_method) as storage_methods
            FROM crypto_holdings
            WHERE username = ?
            GROUP BY crypto_type
            ORDER BY total_amount DESC
        """, [username]).fetchall()
        
        summary = {}
        for row in result:
            crypto_type = row[0]
            summary[crypto_type] = {
                'crypto_type': crypto_type,
                'total_amount': float(row[1]) if row[1] else 0.0,
                'avg_price': float(row[2]) if row[2] else 0.0,
                'wallet_count': int(row[3]) if row[3] else 0,
                'storage_method_count': int(row[4]) if row[4] else 0,
                'first_purchase': row[5],
                'last_purchase': row[6],
                'storage_methods': row[7].split(',') if row[7] else []
            }
        
        return summary

    def get_all_accounts(self, username: str) -> List[Dict]:
        """Get all accounts for a user"""
        result = self.conn.execute("""
            SELECT 
                account_name,
                account_type,
                institution,
                balance,
                currency,
                access_priority,
                access_method,
                days_to_access,
                is_joint,
                notes,
                last_updated
            FROM financial_accounts
            WHERE username = ?
            ORDER BY balance DESC
        """, [username]).fetchall()
        
        accounts = []
        for row in result:
            accounts.append({
                'account_name': row[0],
                'account_type': row[1],
                'institution': row[2],
                'balance': float(row[3]) if row[3] else 0.0,
                'currency': row[4],
                'access_priority': row[5],
                'access_method': row[6],
                'days_to_access': row[7],
                'is_joint': bool(row[8]),
                'notes': row[9],
                'last_updated': row[10]
            })
        
        return accounts
    
    def _get_sovereignty_status(self, ratio: float) -> str:
        """Determine sovereignty status based on ratio"""
        if ratio < 1:
            return "Vulnerable ⚫"
        elif ratio < 3:
            return "Fragile 🔴"
        elif ratio < 6:
            return "Robust 🟡"
        elif ratio < 20:
            return "Antifragile 🟢"
        else:
            return "Generationally Sovereign 🟩"
    
    def save_sovereignty_snapshot(self, username: str, metrics: Dict) -> bool:
        """Save sovereignty calculation snapshot"""
        try:
            self.conn.execute("""
                INSERT INTO sovereignty_snapshot
                (username, total_assets, total_crypto, total_traditional,
                 monthly_expenses, annual_expenses, sovereignty_ratio,
                 full_sovereignty_ratio, sovereignty_status, 
                 emergency_runway_months, btc_price_at_snapshot)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                username,
                metrics['total_assets'],
                metrics['total_crypto_value'],
                metrics['total_assets'] - metrics['total_crypto_value'],
                metrics['monthly_expenses'],
                metrics['annual_expenses'],
                metrics['sovereignty_ratio'],
                metrics['full_sovereignty_ratio'],
                metrics['sovereignty_status'],
                metrics['emergency_runway_months'],
                metrics['btc_price']
            ])
            return True
        except Exception as e:
            print(f"Error saving snapshot: {e}")
            return False