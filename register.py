# register.py
import duckdb, os, bcrypt, json
from flask import Flask, request, jsonify

app = Flask(__name__)

BASE     = os.path.dirname(__file__)
DB_PATH  = os.path.join(BASE, "data", "sovereignty.duckdb")
con      = duckdb.connect(DB_PATH)

@app.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    username = data.get("username", "").strip()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")
    path     = data.get("path", "default")

    if not username or not email or not password:
        return jsonify({"status": "error", "message": "Missing required fields."}), 400

    # Check if user already exists
    existing = con.execute("SELECT COUNT(*) FROM users WHERE username = ? OR email = ?", [username, email]).fetchone()[0]
    if existing > 0:
        return jsonify({"status": "error", "message": "Username or email already exists."}), 409

    # Hash password
    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    # Insert user
    con.execute(
        "INSERT INTO users (username, email, hashed_password, path) VALUES (?, ?, ?, ?)",
        (username, email, hashed_pw, path)
    )

    return jsonify({"status": "success", "message": "User registered!"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)
