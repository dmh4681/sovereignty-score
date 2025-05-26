import os
import duckdb
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE, "data", "sovereignty.duckdb")

def reset_db():
    """Reset the database with correct table structure"""
    try:
        # Delete the database file if it exists
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            logger.info(f"Deleted existing database at {DB_PATH}")
        
        # Create new database
        conn = duckdb.connect(DB_PATH)
        
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
            username            VARCHAR,
            path                VARCHAR,
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
        
        logger.info("Successfully created new database with correct table structure")
        
    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    reset_db() 