# test_flask_bcrypt.py

from flask import Flask
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Sample password
password = "sovereign123"
hashed = bcrypt.generate_password_hash(password).decode('utf-8')

print("✅ Flask and Bcrypt are working!")
print(f"Plaintext password: {password}")
print(f"Hashed password: {hashed}")
print(f"Password match? {bcrypt.check_password_hash(hashed, password)}")
