# family_finance_calculations.py
"""
Enhanced calculation functions for Family Finance Plan
Properly integrates database data without hardcoded values
"""

from typing import Dict, Optional
from datetime import datetime
import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from family_finance_database import FamilyFinanceDB
import btc_price_utils

def calculate_enhanced_emergency_metrics(username: str, path: str, finance_db: FamilyFinanceDB) -> Dict:
    """
    Calculate emergency metrics using real database data
    No hardcoded values - everything from database
    """
    
    # Get current BTC price
    btc_price, price_timestamp = btc_price_utils.get_current_btc_price()
    
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
    
    # Get crypto details - REAL VALUES FROM DATABASE
    crypto_summary = finance_db.get_crypto_summary(username)
    
    # Extract BTC amount from database (not hardcoded!)
    btc_data = crypto_summary.get('BTC', {})
    btc_amount = btc_data.get('total_amount', 0.0)
    btc_avg_price = btc_data.get('avg_price', 0.0)
    
    # Calculate total crypto value across all holdings
    total_crypto_value = sum(
        crypto['total_amount'] * (btc_price if crypto['crypto_type'] == 'BTC' else 0)
        for crypto_type, crypto in crypto_summary.items()
        if isinstance(crypto, dict) and 'total_amount' in crypto
    )
    
    # Get expense data
    expense_summary = finance_db.get_expense_summary(username)
    
    # Build comprehensive emergency data structure
    emergency_data = {
        "username": username,
        "path": path,
        "emergency_runway_months": metrics['emergency_runway_months'],
        "estimated_portfolio_value": metrics['total_assets'],
        "estimated_crypto_value": total_crypto_value,
        "total_btc": btc_amount,
        "total_sats": int(btc_amount * 100_000_000),
        "btc_avg_acquisition_price": btc_avg_price,
        "monthly_expenses": metrics['monthly_expenses'],
        "annual_expenses": metrics['annual_expenses'],
        "immediate_access_estimate": access_totals['immediate'],
        "short_term_access_estimate": access_totals['short_term'],
        "medium_term_access_estimate": access_totals['medium_term'],
        "long_term_access_estimate": access_totals['long_term'],
        "sovereignty_status": metrics['sovereignty_status'],
        "sovereignty_ratio": metrics['sovereignty_ratio'],
        "full_sovereignty_ratio": metrics['full_sovereignty_ratio'],
        "btc_price": btc_price,
        "btc_price_timestamp": price_timestamp,
        "detailed_accounts": accounts,
        "expense_breakdown": expense_summary,
        "crypto_summary": crypto_summary,
        "has_data": btc_amount > 0 or metrics['total_assets'] > 0
    }
    
    # Add data quality indicators
    emergency_data['data_completeness'] = calculate_data_completeness(emergency_data)
    
    return emergency_data

def calculate_data_completeness(data: Dict) -> Dict:
    """
    Calculate how complete the user's financial data is
    """
    completeness = {
        'accounts_setup': data['estimated_portfolio_value'] > 0,
        'crypto_setup': data['total_btc'] > 0 or data['estimated_crypto_value'] > 0,
        'expenses_setup': data['monthly_expenses'] > 0,
        'emergency_access_setup': data['immediate_access_estimate'] > 0,
        'score': 0
    }
    
    # Calculate completeness score
    total_checks = 4
    completed = sum(1 for v in completeness.values() if v is True)
    completeness['score'] = (completed / total_checks) * 100
    completeness['missing_items'] = []
    
    if not completeness['accounts_setup']:
        completeness['missing_items'].append("Financial accounts")
    if not completeness['crypto_setup']:
        completeness['missing_items'].append("Crypto holdings")
    if not completeness['expenses_setup']:
        completeness['missing_items'].append("Monthly expenses")
    if not completeness['emergency_access_setup']:
        completeness['missing_items'].append("Emergency access accounts")
    
    return completeness

def format_sovereignty_status_header(data: Dict) -> str:
    """
    Format the sovereignty status header with dynamic data
    """
    status = data['sovereignty_status']
    ratio = data['sovereignty_ratio']
    monthly = data['monthly_expenses']
    
    # Dynamic status colors based on sovereignty level
    status_colors = {
        'Vulnerable': '#ef4444',      # Red
        'Fragile': '#f59e0b',        # Orange
        'Robust': '#eab308',         # Yellow
        'Antifragile': '#22c55e',    # Green
        'Generationally Sovereign': '#10b981'  # Emerald
    }
    
    bg_color = status_colors.get(status, '#6b7280')
    
    return f"""
    <div style="background: {bg_color}; 
                padding: 20px; 
                border-radius: 10px; 
                margin-bottom: 20px;">
        <h2 style="color: white; margin: 0; text-align: center;">
            Your Sovereignty Status: {status} {'⚫' if status == 'Vulnerable' else '🔴' if status == 'Fragile' else '🟡' if status == 'Robust' else '🟢' if status == 'Antifragile' else '🟩'}
        </h2>
        <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; text-align: center; font-size: 20px;">
            {ratio:.1f} years of financial sovereignty | ${monthly:,.0f}/month expenses
        </p>
    </div>
    """