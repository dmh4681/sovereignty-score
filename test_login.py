import requests
import json

def test_login(email, password, expected_status=200, description=""):
    """Test login with given credentials and print results"""
    print(f"\n=== Testing: {description} ===")
    print(f"Email: {email}")
    print(f"Password: {password}")
    
    data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(
            "http://localhost:5002/login",
            json=data
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        print(f"Test {'PASSED' if response.status_code == expected_status else 'FAILED'}")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Test FAILED")

# Test cases
test_cases = [
    {
        "email": "test@example.com",
        "password": "testpass123",
        "expected_status": 200,
        "description": "Valid credentials"
    },
    {
        "email": "test@example.com",
        "password": "wrongpassword",
        "expected_status": 401,
        "description": "Wrong password"
    },
    {
        "email": "nonexistent@example.com",
        "password": "anypassword",
        "expected_status": 401,
        "description": "Non-existent user"
    },
    {
        "email": "",
        "password": "testpass123",
        "expected_status": 400,
        "description": "Missing email"
    },
    {
        "email": "test@example.com",
        "password": "",
        "expected_status": 400,
        "description": "Missing password"
    },
    {
        "email": "",
        "password": "",
        "expected_status": 400,
        "description": "Missing both email and password"
    }
]

# Run all test cases
print("Starting login tests...")
for test in test_cases:
    test_login(
        test["email"],
        test["password"],
        test["expected_status"],
        test["description"]
    ) 