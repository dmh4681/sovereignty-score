# btc_price_utils.py
"""
Centralized BTC price handling utilities for the Family Finance Plan
Place this file in your main sovereignty-score directory
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, Tuple
from db import get_db_connection

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_current_btc_price() -> Tuple[float, datetime]:
    """
    Get current BTC price from database with proper error handling
    Returns: (price, timestamp)
    """
    try:
        # Use the connection as a context manager
        with get_db_connection() as conn:
            result = conn.execute("""
                SELECT closing_price, date 
                FROM btc_price_history 
                ORDER BY date DESC 
                LIMIT 1
            """).fetchone()
            
            if result and result[0] > 0:
                return float(result[0]), result[1]
            
            # If no recent price, try to get any valid price
            fallback_result = conn.execute("""
                SELECT closing_price, date 
                FROM btc_price_history 
                WHERE closing_price > 0
                ORDER BY date DESC 
                LIMIT 1
            """).fetchone()
            
            if fallback_result and fallback_result[0] > 0:
                return float(fallback_result[0]), fallback_result[1]
                
    except Exception as e:
        # Don't show warning if we're not in a Streamlit context
        try:
            st.warning(f"Unable to fetch BTC price from database: {str(e)}")
        except:
            pass
    
    # Last resort: return a reasonable market estimate
    # This should be updated periodically based on market conditions
    default_price = 95000.0  # As of late 2024/early 2025
    try:
        st.warning(f"Using estimated BTC price of ${default_price:,.0f}. Please update your price data.")
    except:
        pass
    return default_price, datetime.now()

def format_btc_display(btc_amount: float, show_sats: bool = True) -> str:
    """
    Format BTC amount for display with optional sats conversion
    """
    if btc_amount == 0:
        return "0 BTC"
    
    if btc_amount < 0.001 and show_sats:
        sats = int(btc_amount * 100_000_000)
        return f"{sats:,} sats"
    else:
        formatted = f"{btc_amount:.8f}".rstrip('0').rstrip('.')
        return f"{formatted} BTC"

def get_btc_value_with_price(btc_amount: float) -> Tuple[float, float]:
    """
    Get BTC value in USD with current price
    Returns: (usd_value, btc_price)
    """
    btc_price, _ = get_current_btc_price()
    usd_value = btc_amount * btc_price
    return usd_value, btc_price