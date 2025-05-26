# register.py
import duckdb, os, bcrypt, json
from flask import Flask, request, jsonify
import logging
from contextlib import contextmanager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

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
                conn.execute(sql)
                logger.info("Successfully created users table")
        except Exception as e:
            logger.error(f"Error creating users table: {str(e)}")
            raise

@app.route("/register", methods=["POST"])
def register_user():
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
            # Check if user already exists
            existing = conn.execute("SELECT COUNT(*) FROM users WHERE username = ? OR email = ?", [username, email]).fetchone()[0]
            if existing > 0:
                return jsonify({"status": "error", "message": "Username or email already exists."}), 409

            # Hash password
            salt = bcrypt.gensalt()
            hashed_pw = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

            # Insert user
            conn.execute(
                "INSERT INTO users (username, email, password, path) VALUES (?, ?, ?, ?)",
                (username, email, hashed_pw, path)
            )
            logger.info(f"Successfully registered user: {username}")
            return jsonify({"status": "success", "message": "User registered!"}), 200
        except Exception as e:
            logger.error(f"Error during registration: {str(e)}")
            return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500

if __name__ == "__main__":
    logger.info("Starting Flask server...")
    # Initialize database
    init_db()
    app.run(debug=True, port=5001, use_reloader=False)
