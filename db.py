import duckdb
import os
import logging
from contextlib import contextmanager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE, "data", "sovereignty.duckdb")

@contextmanager
def get_db_connection():
    """Get a database connection using a context manager"""
    conn = None
    try:
        conn = duckdb.connect(DB_PATH)
        logger.info("Database connection created")
        yield conn
    except Exception as e:
        logger.error(f"Error creating database connection: {str(e)}")
        raise
    finally:
        if conn:
            try:
                conn.close()
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database connection: {str(e)}")

def init_db():
    """Initialize the database with required tables"""
    with get_db_connection() as conn:
        # Create users table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username    TEXT PRIMARY KEY,
            email       TEXT NOT NULL,
            password    TEXT NOT NULL,
            path        TEXT NOT NULL,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Create sovereignty table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS sovereignty (
            timestamp            TIMESTAMP,
            username             VARCHAR,
            path                 VARCHAR,
            home_cooked_meals    INTEGER,
            junk_food            BOOLEAN,
            exercise_minutes     INTEGER,
            strength_training    BOOLEAN,
            no_spending          BOOLEAN,
            invested_bitcoin     BOOLEAN,
            btc_usd              REAL DEFAULT 0,
            btc_sats             INTEGER DEFAULT 0,
            meditation           BOOLEAN,
            gratitude            BOOLEAN,
            read_or_learned      BOOLEAN,
            environmental_action BOOLEAN,
            score                INTEGER
        );
        """)
        
        # Create btc_price_history table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS btc_price_history (
            date           DATE PRIMARY KEY,
            closing_price  REAL NOT NULL,
            volume         REAL,
            market_cap     REAL,
            created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Create sovereignty_snapshot table (note: singular, not plural)
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
        
        # Check if btc_price_history has any data, if not add a default entry
        result = conn.execute("SELECT COUNT(*) FROM btc_price_history").fetchone()
        if result[0] == 0:
            # Insert a default price (current approximate market price)
            conn.execute("""
                INSERT INTO btc_price_history (date, closing_price, volume, market_cap)
                VALUES (CURRENT_DATE, 95000.0, 0, 0)
            """)
            logger.info("Inserted default BTC price for initialization")
        
        logger.info("Database tables initialized")