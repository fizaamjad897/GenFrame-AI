# Change Report — API Key Implementation

Date: 2026-01-08
Author: GitHub Copilot

## Summary
Implemented secure API key support and tests. Changes include:
- API key generation, hashing (HMAC-SHA256), verification, and deletion.
- Endpoints to create and delete API keys.
- Authentication flow updated to accept `X-API-KEY` header before falling back to JWT.
- Unit tests added to cover create/delete/usage flows.
- `README.md` updated with usage notes. `SECURITY_REPORT.md` updated to include API key best practices.

---

## Files added / modified
- Modified: `auth.py`
  - Added imports: `secrets`, `hmac`, `hashlib`.
  - Added `API_KEY_SECRET` environment variable fallback and helpers:
    - `_hash_api_key(api_key)` — compute HMAC-SHA256 digest using `API_KEY_SECRET`.
    - `generate_api_key_for_user(user_id)` — generate a secure key (`secrets.token_urlsafe(32)`), store its hashed value as `apiKeyHash` in the user's DB document, and return the raw key (only once).
    - `verify_api_key(raw_key)` — verify a raw key by hashing and querying `users_collection` for a matching `apiKeyHash`.
    - `delete_api_key(user_id)` — remove `apiKeyHash` from user doc.

- Modified: `models.py`
  - Added optional `apiKeyHash: Optional[str]` field to the `User` pydantic model.

- Modified: `main.py`
  - Imported `generate_api_key_for_user`, `delete_api_key`, `verify_api_key`.
  - Updated `get_current_user` dependency to support header `X-API-KEY` first (verifies API key via `verify_api_key`), otherwise falls back to Bearer JWT.
  - Added endpoints:
    - `POST /api/users/api-key` — create and return the raw API key (only when user has no active key).
    - `DELETE /api/users/api-key` — delete the active API key.

- Modified: `README.md`
  - Added an "API Keys" section documenting how to create/delete keys and how to authenticate requests with `X-API-KEY`.

- Added file: `verify_api_key_flow.py` — a small script to manually exercise registration + key creation + `GET /api/users/me` using an API key.

- Added tests: `tests/test_api_keys.py` — pytest tests for the key flows.

- Added dev requirements: `requirements-dev.txt` (pytest, pytest-mock)

- Modified: `SECURITY_REPORT.md`
  - Documented API key best practices (HMAC storage, show raw key once, do not log raw keys, rotate server secret, prefer vaults for client storage).

---

## Security considerations implemented
- Raw API keys are generated using `secrets.token_urlsafe(32)` and returned only once directly to the client. The server stores only the HMAC-SHA256 digest using `API_KEY_SECRET`.
- Only one active API key per user is allowed by the server: the creation endpoint fails if `apiKeyHash` exists.
- The header `X-API-KEY` is checked first for each authenticated endpoint; if present it is used to authenticate the user directly.
- The README and Security Report were updated with guidance for clients (store keys in secret manager, rotate keys, do not log raw keys).

---

## Tests
- `tests/test_api_keys.py` covers:
  - Successful creation of API key when none exists (mocked generator)
  - Attempt to create when an active key exists returns HTTP 400
  - Successful deletion and deletion failure flows
  - Using `X-API-KEY` to authenticate `/api/users/me` (valid/invalid key paths)

Run tests locally:
1. Create a venv and activate
2. `pip install -r requirements-dev.txt`
3. `pip install -r requirements.txt` (if you haven't already)
4. `pytest -q`

Note: The tests mock DB-related functions where appropriate and rely on FastAPI's TestClient.

---

## Deployment notes & environment variables
- `API_KEY_SECRET` (optional) — server-side secret used for HMAC of API keys. If not provided, `SECRET_KEY` is used.
- The server will not reveal hashed values — raw keys must be stored by the client in a secure vault.

---

## Next recommended steps
- Add CI pipeline to run `pytest` and SCA checks.
- Add e2e integration tests against a test DB (mongodb test container) for full integration verification.
- Consider adding audit logging when keys are created/deleted and monitoring for suspicious usage patterns.

---

If you'd like, I can now run tests in the environment and add GitHub Actions to run tests on push. Let me know which you'd like me to do next.
