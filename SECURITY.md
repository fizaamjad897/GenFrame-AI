# Security Middleware Implementation

## Overview
This document outlines the comprehensive security middleware implementation for the Visual Engine API, including input validation, rate limiting, and request sanitization.

## Architecture

### Components

```
├── middleware.py       # Security middleware (rate limiting, request validation)
├── validators.py       # Input validation utilities
├── main.py            # Updated with security integration
└── requirements.txt    # Added python-magic-bin
```

## Security Features

### 1. Request Validation Middleware (`middleware.py`)

The `SecurityMiddleware` intercepts **all requests** and performs:

#### Rate Limiting
- **100 requests per minute** per IP address
- **Automatic IP blocking** for rate limit violations
- In-memory storage (use Redis for production scaling)

#### URL Pattern Validation
- Blocks path traversal attempts (`../`)
- Blocks null byte injection (`%00`)
- Blocks XSS attempts (`<script>`)

#### Request Size Limits
- Maximum request body: **20MB**
- Enforced before processing

#### Content-Type Validation
- **File upload endpoints**: Must use `multipart/form-data`
- **JSON endpoints**: Must use `application/json`

#### Security Headers
Automatically adds to all responses:
```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### 2. Input Validators (`validators.py`)

#### Image Upload Validation
- **File size**: Max 10MB per image
- **MIME type verification**: Uses magic bytes (not file extension)
- **Allowed types**: JPEG, PNG, WebP, GIF, BMP
- **Image integrity**: Verifies file can be opened by PIL
- **Dimension limits**: 10px - 10,000px (prevents bombs)

#### String Sanitization
Blocks patterns indicative of:
- **XSS attacks**: `<script>`, `javascript:`, `on*=`
- **SQL injection**: `union`, `select`, `insert`, etc.
- **Path traversal**: `../`, `..\\`
- **Null bytes**: `\x00`

#### Format Validation
- **Email**: RFC-compliant regex
- **Aspect ratio**: `\d+:\d+` format, reasonable ranges (1-100)
- **API keys**: Base64-like format, 40+ characters
- **Prompts**: Max 1000 characters, sanitized

### 3. Endpoint Integration

#### Protected Endpoints

**`/api/resize`**
```python
# Validates:
1. API key scope (must be 'resize')
2. Aspect ratio format
3. Image file (magic bytes, size, integrity)
4. Request size
```

**`/api/create`**
```python
# Validates:
1. API key scope (must be 'create')
2. Prompt content (sanitized, length-checked)
3. Aspect ratio format
4. Optional reference image (same as resize)
```

**`/api/users/api-key`**
```python
# Validates:
1. Key type ('resize' or 'create')
2. JWT authentication
```

## Security Best Practices Implemented

### ✅ Defense in Depth
- **Layer 1**: Middleware (all requests)
- **Layer 2**: Endpoint validators (specific inputs)
- **Layer 3**: Business logic (credit checks, scoping)

### ✅ Input Validation
- **Never trust client input**
- **Whitelist approach** (allowed types, not blocked types)
- **Magic byte verification** (not file extensions)

### ✅ Rate Limiting
- **Per-IP tracking**
- **Automatic blocking** of abusers
- **Configurable limits**

### ✅ Secure Headers
- **XSS protection**
- **Clickjacking protection**
- **MIME-sniffing protection**
- **HSTS enforcement**

### ✅ Error Handling
- **Never expose internal errors** to clients
- **Log suspicious activity** for monitoring
- **Generic error messages** (prevents enumeration)

## Configuration

### Environment Variables

No new environment variables required. The middleware uses sensible defaults:

```python
# Rate limiting
RATE_LIMIT_REQUESTS = 100  # per minute
RATE_LIMIT_WINDOW = 60     # seconds

# File sizes
MAX_IMAGE_SIZE = 10 * 1024 * 1024   # 10MB
MAX_REQUEST_SIZE = 20 * 1024 * 1024  # 20MB
```

### Customization

Edit `middleware.py` to adjust:
- Rate limits
- Blocked URL patterns
- Security headers

Edit `validators.py` to adjust:
- Allowed file types
- Size limits
- Validation patterns

## Usage

### Installation

```bash
pip install -r requirements.txt
```

### Testing

The middleware is **automatically applied** to all requests. Test with:

```bash
# Start server
uvicorn main:app --reload

# The frontend (test_frontend.html) will automatically use the secured endpoints
```

### Monitoring

Suspicious activity is logged to console:

```
[SECURITY] 2026-01-09T20:00:00 - Suspicious activity from 192.168.1.1: Input contains potentially dangerous content
```

In production, route these logs to:
- **SIEM** (Security Information and Event Management)
- **Log aggregation** (ELK, Splunk, etc.)
- **Alert systems** (PagerDuty, Slack, etc.)

## Production Recommendations

### 1. Rate Limiting
Replace in-memory storage with **Redis**:

```python
import redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Use Redis for distributed rate limiting
r.incr(f"rate_limit:{client_ip}")
r.expire(f"rate_limit:{client_ip}", RATE_LIMIT_WINDOW)
```

### 2. HTTPS
Ensure the server is behind SSL/TLS. Update CORS to restrict origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origin
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-API-KEY"],
)
```

### 3. Web Application Firewall (WAF)
Consider adding a WAF like:
- **Cloudflare**
- **AWS WAF**
- **ModSecurity**

### 4. Monitoring & Alerts
Set up real-time alerts for:
- Rate limit violations
- Validation failures
- Suspicious patterns

### 5. Database Security
Ensure MongoDB:
- Uses authentication
- Runs behind a firewall
- Has encrypted connections (TLS)

## Testing the Security

### Valid Requests
```bash
# Should work
curl -X POST http://localhost:8000/api/resize \
  -H "X-API-KEY: your-resize-key" \
  -F "file=@test.jpg" \
  -F "aspect_ratio=16:9"
```

### Blocked Requests

**Rate limit exceeded:**
```bash
# Run >100 requests in 60 seconds
for i in {1..150}; do curl http://localhost:8000/api/users/me; done
# Response: 429 Too Many Requests
```

**Invalid file type:**
```bash
curl -X POST http://localhost:8000/api/resize \
  -H "X-API-KEY: your-key" \
  -F "file=@malicious.exe" \
  -F "aspect_ratio=16:9"
# Response: 400 Bad Request - Invalid file type
```

**XSS attempt in prompt:**
```bash
curl -X POST http://localhost:8000/api/create \
  -H "X-API-KEY: your-key" \
  -F "prompt=<script>alert('xss')</script>" \
  -F "aspect_ratio=1:1"
# Response: 400 Bad Request - Input contains potentially dangerous content
```

**Oversized file:**
```bash
# File > 10MB
curl -X POST http://localhost:8000/api/resize \
  -H "X-API-KEY: your-key" \
  -F "file=@huge_image.jpg" \
  -F "aspect_ratio=16:9"
# Response: 400 Bad Request - File size exceeds maximum
```

## Compliance

This implementation provides baseline security for:
- **OWASP Top 10** protection
- **PCI DSS** (if processing payments)
- **GDPR** (data protection measures)
- **SOC 2** (security controls)

## Summary

The security middleware provides **enterprise-grade protection** with:

✅ **Rate limiting** - Prevents DDoS and brute force  
✅ **Input validation** - Prevents injection attacks  
✅ **File verification** - Prevents malicious uploads  
✅ **Request sanitization** - Prevents XSS and path traversal  
✅ **Security headers** - Protects client browsers  
✅ **Logging** - Enables threat detection  

All security measures are **transparent to legitimate users** while blocking malicious activity.
