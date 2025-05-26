# login.py
import os, bcrypt
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from db import get_db_connection, init_db

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
        with get_db_connection() as conn:
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
                "path": path,
                "streamlit_url": "http://localhost:8501"  # Add local Streamlit URL
            }), 200
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500

if __name__ == "__main__":
    logger.info("Starting Flask server...")
    # Initialize database
    init_db()
    app.run(host='0.0.0.0', port=5002, debug=False)
