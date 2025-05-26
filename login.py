# login.py
import duckdb, os, bcrypt
from flask import Flask, request, jsonify

app = Flask(__name__)

BASE     = os.path.dirname(__file__)
DB_PATH  = os.path.join(BASE, "data", "sovereignty.duckdb")
con      = duckdb.connect(DB_PATH)

@app.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = con.execute(
        "SELECT username, password, path FROM users WHERE email = ?", [email]
    ).fetchone()

    if not user:
        return jsonify({"status": "error", "message": "Invalid credentials."}), 401

    username, hashed_pw, path = user
    if not bcrypt.checkpw(password.encode("utf-8"), hashed_pw.encode("utf-8")):
        return jsonify({"status": "error", "message": "Invalid credentials."}), 401

    return jsonify({
        "status": "success",
        "username": username,
        "path": path
    }), 200

if __name__ == "__main__":
    app.run(debug=True, port=5002)
