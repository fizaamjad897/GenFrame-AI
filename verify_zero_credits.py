import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_signup_zero_credits():
    email = f"test_user_zero_{int(time.time())}@example.com"
    password = "testpassword123"
    
    print(f"Testing signup for: {email}")
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/users/register", json={
            "email": email,
            "password": password,
            "fullName": "Test User Zero",
            "fingerprint": "test-zero-credits"
        })
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            user = data.get("user", {})
            max_units = user.get("maxUnits")
            print(f"✅ Success! New user maxUnits: {max_units}")
            if max_units == 0:
                print("✨ Verification PASSED: New user has 0 credits.")
            else:
                print(f"❌ Verification FAILED: Expected 0, got {max_units}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_signup_zero_credits()
