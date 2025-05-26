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
            email                VARCHAR,
            path                 VARCHAR,
            home_cooked_meals    INTEGER,
            junk_food            BOOLEAN,
            exercise_minutes     INTEGER,
            strength_training    BOOLEAN,
            no_spending          BOOLEAN,
            invested_bitcoin     BOOLEAN,
            meditation           BOOLEAN,
            gratitude            BOOLEAN,
            read_or_learned      BOOLEAN,
            environmental_action BOOLEAN,
            score                INTEGER
        );
        """)
        logger.info("Database tables initialized") 