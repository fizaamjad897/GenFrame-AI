"""
Security middleware for request validation and rate limiting
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import Headers
import time
from collections import defaultdict
from datetime import datetime, timedelta
import re
from validators import ValidationError, MAX_REQUEST_SIZE

# Rate limiting storage (in-memory, use Redis for production)
request_counts = defaultdict(lambda: {"count": 0, "reset_time": time.time()})
suspicious_ips = set()

# Rate limit configuration
RATE_LIMIT_REQUESTS = 100  # requests
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_BURST = 10  # max requests in 1 second

# Blocked patterns in URLs
BLOCKED_URL_PATTERNS = [
    re.compile(r'\.\./', re.IGNORECASE),  # Path traversal
    re.compile(r'%00', re.IGNORECASE),  # Null byte injection
    re.compile(r'<script', re.IGNORECASE),  # XSS attempts
]


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive security middleware that validates:
    - Request size limits
    - Rate limiting per IP
    - Malicious URL patterns
    - Required security headers
    - Content-Type validation
    """
    
    async def dispatch(self, request: Request, call_next):
        client_ip = self.get_client_ip(request)
        print(f"🔥 [REQUEST] {request.method} {request.url.path} from {client_ip}")
        
        try:
            # 1. Check if IP is blocked
            if client_ip in suspicious_ips:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Access denied due to suspicious activity"}
                )
            
            # 2. Validate URL for malicious patterns
            self.validate_url(request.url.path)
            
            # 3. Rate limiting
            self.check_rate_limit(client_ip, request.url.path)
            
            # 4. Validate request size
            await self.validate_request_size(request)
            
            # 5. Validate Content-Type for specific endpoints
            self.validate_content_type(request)
            
            # 6. Process request
            response = await call_next(request)
            
            # 7. Add security headers to response
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
            return response
            
        except HTTPException as e:
            raise e
        except ValidationError as e:
            # Log suspicious activity
            self.log_suspicious_activity(client_ip, str(e))
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": str(e)}
            )
        except Exception as e:
            # Log error
            print(f"Middleware error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"}
            )
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check for proxy headers
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client
        return request.client.host if request.client else "unknown"
    
    def validate_url(self, path: str):
        """Check for malicious URL patterns"""
        for pattern in BLOCKED_URL_PATTERNS:
            if pattern.search(path):
                raise ValidationError("Malicious URL pattern detected")
    
    def check_rate_limit(self, client_ip: str, path: str):
        """
        Implement rate limiting per IP address
        """
        current_time = time.time()
        rate_data = request_counts[client_ip]
        
        # Reset counter if window expired
        if current_time - rate_data["reset_time"] > RATE_LIMIT_WINDOW:
            rate_data["count"] = 0
            rate_data["reset_time"] = current_time
        
        # Increment counter
        rate_data["count"] += 1
        
        # Check if limit exceeded
        if rate_data["count"] > RATE_LIMIT_REQUESTS:
            # Block IP temporarily
            suspicious_ips.add(client_ip)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
    
    async def validate_request_size(self, request: Request):
        """Validate request body size"""
        content_length = request.headers.get("content-length")
        
        if content_length:
            content_length = int(content_length)
            if content_length > MAX_REQUEST_SIZE:
                raise ValidationError(
                    f"Request body too large: {content_length} bytes (max: {MAX_REQUEST_SIZE} bytes)"
                )
    
    def validate_content_type(self, request: Request):
        """Validate Content-Type for specific endpoints"""
        path = request.url.path
        method = request.method
        
        # For file upload endpoints
        if path in ["/api-v2/resize", "/api-v2/create"] and method == "POST":
            content_type = request.headers.get("content-type", "")
            if not content_type.startswith("multipart/form-data"):
                raise ValidationError(
                    f"Invalid Content-Type for file upload endpoint: {content_type}"
                )
        
        # For JSON endpoints
        json_endpoints = ["/api-v2/users/register", "/api-v2/users/login"]
        if path in json_endpoints and method == "POST":
            content_type = request.headers.get("content-type", "")
            if "application/json" not in content_type:
                raise ValidationError(
                    f"Invalid Content-Type for JSON endpoint: {content_type}"
                )
    
    def log_suspicious_activity(self, client_ip: str, reason: str):
        """Log suspicious activity for monitoring"""
        timestamp = datetime.utcnow().isoformat()
        print(f"[SECURITY] {timestamp} - Suspicious activity from {client_ip}: {reason}")
        
        # In production, you would:
        # - Log to file/database
        # - Send alerts
        # - Update WAF rules


def cleanup_rate_limits():
    """
    Periodic cleanup of old rate limit data
    Call this function periodically (e.g., every hour)
    """
    current_time = time.time()
    to_remove = []
    
    for ip, data in request_counts.items():
        if current_time - data["reset_time"] > RATE_LIMIT_WINDOW * 2:
            to_remove.append(ip)
    
    for ip in to_remove:
        del request_counts[ip]
    
    # Clear suspicious IPs after some time (e.g., 1 hour)
    suspicious_ips.clear()
