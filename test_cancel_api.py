#!/usr/bin/env python3
"""
Quick test of cancel subscription API
"""

import requests
import json

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2OTZmOTEyYTgxOGRlN2Y2OGMzYTBhMWMiLCJleHAiOjE3Njk2MDczMjd9.suam3acIdcXym5tcLFoc9sfgIMk8ialllCm6lnF64So"

url = "http://localhost:8000/api/stripe/cancel-subscription"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
body = {"at_period_end": False}

print("Testing Cancel Subscription API\n")
print(f"URL: {url}")
print(f"Token: {token[:50]}...\n")

try:
    response = requests.post(url, headers=headers, json=body)
    
    print(f"Status: {response.status_code}")
    print(f"Response:\n")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        print("\n✅ SUCCESS! Subscription cancelled!")
    else:
        print(f"\n❌ Error: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")
