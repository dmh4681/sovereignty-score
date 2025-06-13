# add_missing_tables.py
"""
Script to add missing tables to existing database
"""

import duckdb
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_missing_tables(db_path: str = "sovereignty_tracker.db"):
    """Add missing tables to existing database"""
    
    conn = duckdb.connect(db_path)
    
    try:
        # Add btc_price_history table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS btc_price_history (
            date           DATE PRIMARY KEY,
            closing_price  REAL NOT NULL,
            volume         REAL,
            market_cap     REAL,
            created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        logger.info("Created btc_price_history table")
        
        # Check if it needs default data
        result = conn.execute("SELECT COUNT(*) FROM btc_price_history").fetchone()
        if result[0] == 0:
            conn.execute("""
                INSERT INTO btc_price_history (date, closing_price, volume, market_cap)
                VALUES (CURRENT_DATE, 95000.0, 0, 0)
            """)
            logger.info("Added default BTC price")
        
        # Also ensure sovereignty_snapshot table exists
        conn.execute("""
        CREATE TABLE IF NOT EXISTS sovereignty_snapshot (
            username                    TEXT NOT NULL,
            snapshot_date              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_assets               REAL,
            total_crypto               REAL,
            total_traditional          REAL,
            monthly_expenses           REAL,
            annual_expenses            REAL,
            sovereignty_ratio          REAL,
            full_sovereignty_ratio     REAL,
            sovereignty_status         TEXT,
            emergency_runway_months    REAL,
            btc_price_at_snapshot      REAL,
            PRIMARY KEY (username, snapshot_date)
        );
        """)
        logger.info("Created sovereignty_snapshot table")
        
        conn.close()
        print("✅ Successfully added missing tables!")
        
    except Exception as e:
        logger.error(f"Error adding tables: {e}")
        conn.close()
        raise

if __name__ == "__main__":
    add_missing_tables()