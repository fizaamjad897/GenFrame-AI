# Project Checklist — Visual Engine Backend ✅

This document contains the prioritized checklist of critical fixes, suggested code snippets, and tests to apply to the Visual Engine Backend repository.

---

## Overview
- **Purpose:** Fix critical bugs, improve reliability and security, add tests & CI, and improve developer ergonomics for local development.
- **Priority:** Critical → High → Medium → Low.

---

## Critical fixes (apply first) ⚠️
1. **Fix broken route**
   - File: `main.py`
   - Problem: missing leading slash in decorator `@app.get("api/users/me")`
   - Change to:
     ```py
     @app.get("/api/users/me", response_model=UserResponse)
     async def get_current_user_info(current_user = Depends(get_current_user)):
         return user_doc_to_response(current_user)
     ```

2. **Lazy-init Digital Ocean Spaces client (avoid crash on import)**
   - File: `main.py`
   - Replace inline raises at import with a `get_s3_client()` helper that initializes the client on demand and raises only when upload is attempted.
   - Example helper:
     ```py
     s3_client = None

     def get_s3_client():
         global s3_client
         if s3_client:
             return s3_client

         if not (DO_SPACES_ENDPOINT and DO_SPACES_BUCKET_NAME and DO_SPACES_ACCESS_KEY and DO_SPACES_SECRET_KEY):
             raise RuntimeError("Digital Ocean Spaces not configured. Set ENDPOINT, SPACENAME, ACCESS_KEY_ID, SECRET_KEY.")

         endpoint_clean = DO_SPACES_ENDPOINT.replace('https://', '').replace('http://', '').strip()
         region = endpoint_clean.split('.')[0] if '.' in endpoint_clean else 'nyc3'
         endpoint_url = endpoint_clean if endpoint_clean.startswith('http') else f'https://{endpoint_clean}'

         s3_client = boto3.client(...)
         logging.info("Digital Ocean Spaces client initialized")
         return s3_client
     ```
   - Call `get_s3_client()` inside the `resize_image` flow before upload and handle exceptions with `HTTPException`.

3. **Deterministic signup credits**
   - File: `auth.py` (function `create_user`)
   - Add an env var `DEFAULT_SIGNUP_CREDITS` (default `50`) and set `maxUnits` accordingly so tests and verification scripts behave consistently.
   - Example snippet:
     ```py
     DEFAULT_SIGNUP_CREDITS = int(os.getenv("DEFAULT_SIGNUP_CREDITS", "50"))

     user_doc = {
         "email": user_data.email,
         "password": hash_password(user_data.password),
         "fullName": user_data.fullName or "",
         "fingerprint": user_data.fingerprint,
         "presentationId": user_data.presentationId,
         "plan": "Free Tier",
         "units": 0,
         "maxUnits": DEFAULT_SIGNUP_CREDITS,
         "createdAt": datetime.utcnow(),
         "updatedAt": datetime.utcnow(),
     }
     ```

4. **Only increment units on successful operations**
   - File: `main.py`
   - Move `increment_user_units(...)` to the success path (after successful upload) and call `log_usage(..., success=True)` there. Log failed attempts with `success=False` in exception handlers.

---

## High-priority improvements 🛠️
- Replace `print()` with structured `logging` across `main.py`, `auth.py`, and scripts.
- Validate production secrets (fail-fast in production but allow safer local dev behavior via `ENV` or `DEV_MODE`).
- Add proper input validation and stricter JWT checks if needed.

---

## Tests to add (pytest) 🧪
1. **Registration test** — assert `maxUnits` equals `DEFAULT_SIGNUP_CREDITS`.
   ```py
   def test_register_assigns_default_credits(client):
       resp = client.post('/api/users/register', json={...})
       assert resp.status_code == 200
       assert resp.json()['user']['maxUnits'] == int(os.getenv('DEFAULT_SIGNUP_CREDITS', '50'))
   ```

2. **User me route** — test `/api/users/me` using `TestClient` and mocked auth dependency.
3. **Resize endpoint** — mock `genai.Client` and `get_s3_client().put_object`:
   - Successful path: returns JSON with URL and increments units.
   - Failure path: returns `HTTP 500` and logs usage with `success=False`.

Add `pytest` and `pytest-mock` to `requirements-dev.txt` or similar.

---

## Medium / housekeeping ✅
- Remove duplicate `python-multipart` in `requirements.txt` and pin dependency versions.
- Add `CONTRIBUTING.md` with setup and test instructions.
- Update `README.md` to document `DEFAULT_SIGNUP_CREDITS` and lazy DO behavior.

---

## How to apply (minimal safe steps)
1. Fix route and remove stray return in `main.py`.
2. Add `get_s3_client()` helper and replace import-time raises.
3. Update `create_user()` to use `DEFAULT_SIGNUP_CREDITS`.
4. Move `increment_user_units()` to the success path and update logging.
5. Add pytest tests and run them locally.

Run commands:
- `uvicorn main:app --reload`
- `python seed_plans.py`
- `python setup_client_account.py`
- `pytest -q`

---

## Notes
- I can implement these changes and add the tests on request; this file is intended to be the minimal, exact checklist for quick application.

---

Created by: GitHub Copilot (Raptor mini (Preview))
