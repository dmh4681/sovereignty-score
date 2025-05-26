# login.py
import duckdb, os, bcrypt
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import atexit
import signal
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Enable CORS for all routes with more permissive settings
CORS(app, 
     resources={r"/*": {
         "origins": ["https://dmh4681.github.io", 
                    "http://localhost:5000", 
                    "http://127.0.0.1:5000", 
                    "http://localhost:8501", 
                    "http://127.0.0.1:8501"],
         "methods": ["GET", "POST", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization", "Accept"],
         "supports_credentials": True
     }})

BASE     = os.path.dirname(__file__)
DB_PATH  = os.path.join(BASE, "data", "sovereignty.duckdb")
SQL_FILE = os.path.join(BASE, "config", "create_users_table.sql")

# Global connection pool
_db_connection = None

def cleanup():
    """Cleanup function to close database connection"""
    global _db_connection
    if _db_connection is not None:
        try:
            _db_connection.close()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {str(e)}")
        finally:
            _db_connection = None

def get_db_connection():
    """Get or create a database connection"""
    global _db_connection
    try:
        if _db_connection is None:
            _db_connection = duckdb.connect(DB_PATH)
            logger.info("New database connection created")
        return _db_connection
    except Exception as e:
        logger.error(f"Error creating database connection: {str(e)}")
        # Try to clean up any existing connection
        cleanup()
        # Try one more time
        _db_connection = duckdb.connect(DB_PATH)
        return _db_connection

def init_db():
    """Initialize the database with required tables"""
    try:
        conn = get_db_connection()
        logger.info(f"Reading SQL file from: {SQL_FILE}")
        with open(SQL_FILE, 'r') as f:
            sql = f.read()
            logger.info(f"SQL to execute: {sql}")
            conn.execute(sql)
            logger.info("Successfully created users table")
    except Exception as e:
        logger.error(f"Error creating users table: {str(e)}")
        raise

@app.route("/login", methods=["POST", "OPTIONS"])
def login_user():
    if request.method == "OPTIONS":
        return "", 200
        
    logger.info("Received login request")
    logger.info(f"Request headers: {dict(request.headers)}")
    logger.info(f"Request data: {request.get_data()}")
    
    try:
        data = request.get_json()
        logger.info(f"Parsed JSON data: {data}")
    except Exception as e:
        logger.error(f"Error parsing JSON: {str(e)}")
        return jsonify({"status": "error", "message": "Invalid JSON data"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    logger.info(f"Processing login for username: {username}")

    # Validate input fields
    if not username or not password:
        logger.warning("Missing username or password")
        return jsonify({
            "status": "error",
            "message": "Username and password are required."
        }), 400

    try:
        conn = get_db_connection()
        user = conn.execute(
            "SELECT username, password, path FROM users WHERE username = ?", [username]
        ).fetchone()

        if not user:
            logger.warning(f"User not found: {username}")
            return jsonify({"status": "error", "message": "Invalid credentials."}), 401

        db_username, hashed_pw, path = user
        if not bcrypt.checkpw(password.encode("utf-8"), hashed_pw.encode("utf-8")):
            logger.warning(f"Invalid password for user: {username}")
            return jsonify({"status": "error", "message": "Invalid credentials."}), 401

        logger.info(f"Successful login for user: {db_username}")
        return jsonify({
            "status": "success",
            "username": db_username,
            "path": path
        }), 200
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("Received shutdown signal")
    cleanup()
    sys.exit(0)

if __name__ == "__main__":
    # Register cleanup handlers
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Starting Flask server...")
    # Initialize database
    init_db()
    # Disable debug mode to prevent auto-reloading
    app.run(host='0.0.0.0', port=5002, debug=False)
