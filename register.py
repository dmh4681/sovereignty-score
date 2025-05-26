# register.py
import duckdb, os, bcrypt, json
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from contextlib import contextmanager
import subprocess
from backup_db import create_backup

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Enable CORS for all routes
CORS(app, 
     resources={r"/*": {
         "origins": ["https://dmh4681.github.io", 
                    "https://sovereignty-score-digitalnomad.streamlit.app",
                    "http://localhost:5000", 
                    "http://127.0.0.1:5000", 
                    "http://localhost:8501", 
                    "http://127.0.0.1:8501"],
         "methods": ["GET", "POST", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization", "Accept", "Origin"],
         "supports_credentials": True
     }})

BASE     = os.path.dirname(__file__)
DB_PATH  = os.path.join(BASE, "data", "sovereignty.duckdb")
SQL_FILE = os.path.join(BASE, "config", "create_users_table.sql")

# Ensure data directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = None
    try:
        conn = duckdb.connect(DB_PATH)
        yield conn
    finally:
        if conn:
            conn.close()

def init_db():
    """Initialize the database with required tables"""
    with get_db() as conn:
        try:
            logger.info(f"Reading SQL file from: {SQL_FILE}")
            with open(SQL_FILE, 'r') as f:
                sql = f.read()
                logger.info(f"SQL to execute: {sql}")
                # Drop the table if it exists to ensure clean state
                conn.execute("DROP TABLE IF EXISTS users")
                # Create the table
                conn.execute(sql)
                # Print the table structure
                table_info = conn.execute("DESCRIBE users").fetchall()
                logger.info(f"Table structure after creation: {table_info}")
                logger.info("Successfully created users table")
        except Exception as e:
            logger.error(f"Error creating users table: {str(e)}")
            raise

@app.route("/register", methods=["POST", "OPTIONS"])
def register_user():
    if request.method == "OPTIONS":
        return "", 200
        
    logger.info("Received registration request")
    data = request.get_json()
    username = data.get("username", "").strip()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")
    path     = data.get("path", "default")

    logger.info(f"Processing registration for user: {username}")

    if not username or not email or not password:
        return jsonify({"status": "error", "message": "Missing required fields."}), 400

    with get_db() as conn:
        try:
            # Print current table structure
            table_info = conn.execute("DESCRIBE users").fetchall()
            logger.info(f"Current table structure before registration: {table_info}")
            
            # Check if user already exists
            existing = conn.execute("SELECT COUNT(*) FROM users WHERE username = ? OR email = ?", [username, email]).fetchone()[0]
            if existing > 0:
                return jsonify({"status": "error", "message": "Username or email already exists."}), 409

            # Hash password
            salt = bcrypt.gensalt()
            hashed_pw = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

            # Insert user
            insert_sql = "INSERT INTO users (username, email, password, path) VALUES (?, ?, ?, ?)"
            logger.info(f"Executing SQL: {insert_sql}")
            logger.info(f"With values: username={username}, email={email}, path={path}")
            conn.execute(insert_sql, (username, email, hashed_pw, path))
            logger.info(f"Successfully registered user: {username}")
            
            # Create backup after successful registration
            if create_backup():
                logger.info("Database backup created successfully")
            else:
                logger.warning("Database backup failed")
                
            return jsonify({"status": "success", "message": "User registered!"}), 200
        except Exception as e:
            logger.error(f"Error during registration: {str(e)}")
            return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500

@app.route("/welcome", methods=["POST", "OPTIONS"])
def welcome_user():
    if request.method == "OPTIONS":
        return "", 200
        
    """Handle the AI welcome script for new users"""
    logger.info("Received welcome request")
    data = request.get_json()
    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    path = data.get("path", "default")

    logger.info(f"Processing welcome for user: {username}")

    if not username or not email:
        return jsonify({"status": "error", "message": "Missing required fields."}), 400

    try:
        # Run the AI welcome script
        script_path = os.path.join(BASE, "AI_Assist_Welcome.py")
        if not os.path.exists(script_path):
            logger.error(f"Welcome script not found at: {script_path}")
            return jsonify({"status": "error", "message": "Welcome script not found."}), 500

        # Run the script with the user's info
        result = subprocess.run(
            ["python", script_path, username, email, path],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            logger.info(f"Welcome script completed successfully for {username}")
            return jsonify({
                "status": "success",
                "message": "Welcome email sent!",
                "output": result.stdout
            }), 200
        else:
            logger.error(f"Welcome script failed for {username}: {result.stderr}")
            return jsonify({
                "status": "error",
                "message": "Failed to send welcome email.",
                "error": result.stderr
            }), 500

    except Exception as e:
        logger.error(f"Error during welcome process: {str(e)}")
        return jsonify({"status": "error", "message": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    logger.info("Starting Flask server...")
    # Initialize database
    init_db()
    app.run(debug=True, port=5001, use_reloader=False)
