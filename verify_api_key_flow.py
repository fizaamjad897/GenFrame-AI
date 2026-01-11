import requests, time

API_BASE_URL = "http://localhost:8000"

email = f"api_key_test_{int(time.time())}@example.com"
password = "testpassword123"

print(f"Registering {email}")
resp = requests.post(f"{API_BASE_URL}/api/users/register", json={
    "email": email,
    "password": password,
    "fullName": "API Key Tester",
})
print(resp.status_code, resp.text)

if resp.status_code != 200:
    print("Registration failed; aborting")
    exit(1)

login = requests.post(f"{API_BASE_URL}/api/users/login", json={
    "email": email,
    "password": password
})
print(login.status_code, login.text)
if login.status_code != 200:
    print("Login failed; aborting")
    exit(1)

token = login.json()["access_token"]

# Create API key
headers = {"Authorization": f"Bearer {token}"}
create = requests.post(f"{API_BASE_URL}/api/users/api-key", headers=headers)
print(create.status_code, create.text)
if create.status_code != 200:
    print("API key creation failed; aborting")
    exit(1)

api_key = create.json().get("api_key")
print("Received API key (store securely):", api_key)

# Use API key to call /api/users/me
headers = {"X-API-KEY": api_key}
me = requests.get(f"{API_BASE_URL}/api/users/me", headers=headers)
print("Call with API key ->", me.status_code, me.text)

# Cleanup: delete API key
headers = {"Authorization": f"Bearer {token}"}
del_resp = requests.delete(f"{API_BASE_URL}/api/users/api-key", headers=headers)
print("Delete key ->", del_resp.status_code, del_resp.text)
