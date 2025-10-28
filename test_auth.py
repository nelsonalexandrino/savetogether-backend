"""
Simple test script to verify authentication endpoints
"""
import requests
import json

BASE_URL = "http://localhost:5000/api/auth"

def test_register():
    """Test user registration"""
    print("Testing registration...")
    response = requests.post(
        f"{BASE_URL}/register",
        headers={"Content-Type": "application/json"},
        json={
            "email": "test@example.com",
            "password": "password123",
            "display_name": "Test User"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    return response.json().get('access_token')

def test_login():
    """Test user login"""
    print("Testing login...")
    response = requests.post(
        f"{BASE_URL}/login",
        headers={"Content-Type": "application/json"},
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    return response.json().get('access_token')

def test_get_profile(token):
    """Test getting user profile"""
    print("Testing get profile...")
    response = requests.get(
        f"{BASE_URL}/profile",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

if __name__ == "__main__":
    print("=" * 50)
    print("Authentication Endpoint Tests")
    print("=" * 50 + "\n")
    
    # Test registration
    try:
        token = test_register()
    except Exception as e:
        print(f"Registration error: {e}")
        print("User might already exist, trying login...\n")
        token = test_login()
    
    # Test login
    if not token:
        token = test_login()
    
    # Test get profile
    if token:
        test_get_profile(token)
    else:
        print("No token available, skipping profile test")
