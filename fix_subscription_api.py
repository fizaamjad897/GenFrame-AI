"""
Simple script to manually update user subscription using the backend API
This avoids MongoDB connection issues by using the running backend server
"""
import requests
import sys

def fix_subscription_via_api(email, backend_url="http://localhost:8000"):
    """Fix subscription by calling the backend API"""
    
    print(f"\n🔍 Fixing subscription for: {email}")
    print(f"📡 Using backend: {backend_url}\n")
    
    try:
        # Call the manual sync endpoint
        response = requests.post(
            f"{backend_url}/api/stripe/manual-sync",
            json={"email": email}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS!\n")
            print(f"   Plan: {data.get('plan', 'Unknown')}")
            print(f"   Credits: {data.get('credits', 0)}")
            print(f"   Subscription ID: {data.get('subscription_id', 'None')}")
            print(f"\n🎉 You can now use your account!")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to backend at {backend_url}")
        print(f"   Make sure your backend is running:")
        print(f"   cd d:\\Visual-Engine\\Secure\\Visual-Engine-BE")
        print(f"   python -m uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        email = input("Enter your email address: ")
    
    fix_subscription_via_api(email)
