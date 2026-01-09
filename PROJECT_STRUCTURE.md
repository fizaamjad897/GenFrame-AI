# Project Structure - Security Enhanced

## New File Organization

```
Visual-Engine-BE/
├── main.py                  # FastAPI app with security integration
├── middleware.py            # NEW: Security middleware (rate limiting, validation)
├── validators.py            # NEW: Input validation utilities
├── auth.py                  # Authentication & authorization
├── models.py                # Pydantic data models
├── seed_plans.py           # Database seeding
├── requirements.txt         # Dependencies (+ python-magic-bin)
├── SECURITY.md             # NEW: Security documentation
├── test_frontend.html      # Testing interface
└── .env                    # Environment configuration
```

## Security Layers

### Layer 1: Middleware (All Requests)
**File:** `middleware.py`
- Rate limiting (100 req/min per IP)
- URL pattern validation
- Request size limits
- Content-Type validation
- Security headers injection

### Layer 2: Input Validators (Specific Inputs)
**File:** `validators.py`
- Image upload validation (magic bytes, size, integrity)
- String sanitization (XSS, SQL injection prevention)
- Format validation (email, aspect ratio, API keys)
- Prompt validation and sanitization

### Layer 3: Business Logic (Endpoints)
**File:** `main.py`
- API key scoping (resize vs create)
- Credit deduction
- Authentication enforcement

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# The new dependency is:
# python-magic-bin - For MIME type verification using magic bytes
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the server:**
   ```bash
   uvicorn main:app --reload
   ```

3. **Test with frontend:**
   Open `test_frontend.html` in your browser

## What Changed

### Added Files
1. **middleware.py** - Security middleware that intercepts all requests
2. **validators.py** - Comprehensive input validation functions
3. **SECURITY.md** - Detailed security documentation

### Modified Files
1. **main.py**
   - Added `SecurityMiddleware`
   - Integrated validators into endpoints
   - Restricted CORS headers to specific values
   
2. **requirements.txt**
   - Added `python-magic-bin` for file type verification

## Security Features

✅ **Rate Limiting** - 100 requests per minute per IP  
✅ **File Validation** - Magic byte verification, not extensions  
✅ **Input Sanitization** - Prevents XSS, SQL injection  
✅ **Request Size Limits** - Max 20MB per request  
✅ **Security Headers** - XSS protection, clickjacking prevention  
✅ **Logging** - Suspicious activity tracking  

## Testing Security

See `SECURITY.md` for comprehensive testing examples.

### Quick Test
```bash
# Valid request (should work)
curl -X POST http://localhost:8000/api/resize \
  -H "X-API-KEY: your-resize-key" \
  -F "file=@test.jpg" \
  -F "aspect_ratio=16:9"

# Rate limit test (will be blocked after 100 requests)
for i in {1..150}; do curl http://localhost:8000/; done
```

## Migration Notes

If you have an existing installation:

1. **Pull latest code**
2. **Install new dependency:** `pip install python-magic-bin`
3. **Restart server** - Middleware activates automatically

**No database migration required** - All changes are application-level.

## For Developers

### Adding New Endpoints

When creating new endpoints:

1. **Validate all inputs** using functions from `validators.py`:
   ```python
   from validators import validate_prompt, ValidationError
   
   try:
       clean_prompt = validate_prompt(user_input)
   except ValidationError as e:
       raise HTTPException(status_code=400, detail=str(e))
   ```

2. **Leverage middleware** - It handles rate limiting and basic validation automatically

3. **Follow principle of least privilege** - Only grant what's necessary

### Customizing Security

**Rate limits** - Edit `middleware.py`:
```python
RATE_LIMIT_REQUESTS = 100  # Adjust as needed
RATE_LIMIT_WINDOW = 60     # seconds
```

**File size limits** - Edit `validators.py`:
```python
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # Adjust as needed
MAX_REQUEST_SIZE = 20 * 1024 * 1024
```

**Allowed file types** - Edit `validators.py`:
```python
ALLOWED_IMAGE_TYPES = [
    "image/jpeg",
    "image/png",
    # Add more types as needed
]
```

## Production Checklist

Before deploying to production:

- [ ] Replace in-memory rate limiting with Redis
- [ ] Configure CORS to specific domains
- [ ] Enable HTTPS/TLS
- [ ] Set up logging to SIEM
- [ ] Configure monitoring and alerts
- [ ] Review and harden MongoDB security
- [ ] Set strong secrets in `.env`
- [ ] Consider adding a WAF (Cloudflare, AWS WAF)

See `SECURITY.md` for detailed production recommendations.

## Support

For security-related questions, see `SECURITY.md`.

For general questions, refer to the main `README.md`.
