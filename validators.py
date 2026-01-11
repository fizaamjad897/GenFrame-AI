"""
Input validation utilities for enhanced security
"""
import re
from typing import Optional, List
from fastapi import UploadFile, HTTPException
import magic  # python-magic for file type detection
from PIL import Image
import io

# Allowed image MIME types
ALLOWED_IMAGE_TYPES = [
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/bmp"
]

# Maximum file sizes (in bytes)
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_REQUEST_SIZE = 20 * 1024 * 1024  # 20MB

# Validation patterns
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
ASPECT_RATIO_PATTERN = re.compile(r'^\d+:\d+$')
API_KEY_PATTERN = re.compile(r'^[A-Za-z0-9_-]{40,}$')

# Dangerous patterns to block
DANGEROUS_PATTERNS = [
    re.compile(r'<script', re.IGNORECASE),
    re.compile(r'javascript:', re.IGNORECASE),
    re.compile(r'on\w+\s*=', re.IGNORECASE),  # Event handlers
    re.compile(r'(\.\./|\.\.\\)', re.IGNORECASE),  # Path traversal
    re.compile(r'(union|select|insert|update|delete|drop|create|alter)\s', re.IGNORECASE),  # SQL keywords
]


class ValidationError(Exception):
    """Custom validation error"""
    pass


def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email or len(email) > 255:
        return False
    return bool(EMAIL_PATTERN.match(email))


def validate_aspect_ratio(ratio: str) -> bool:
    """Validate aspect ratio format (e.g., 16:9, 1:1)"""
    if not ratio or len(ratio) > 10:
        return False
    
    if not ASPECT_RATIO_PATTERN.match(ratio):
        return False
    
    # Parse and validate reasonable ranges
    try:
        parts = ratio.split(':')
        width, height = int(parts[0]), int(parts[1])
        if width <= 0 or height <= 0 or width > 100 or height > 100:
            return False
        return True
    except:
        return False


def sanitize_string(text: str, max_length: int = 500) -> str:
    """
    Sanitize string input to prevent XSS and injection attacks
    """
    if not text:
        return ""
    
    # Limit length
    text = text[:max_length]
    
    # Check for dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if pattern.search(text):
            raise ValidationError("Input contains potentially dangerous content")
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def validate_prompt(prompt: str) -> str:
    """Validate and sanitize prompt input"""
    if not prompt:
        raise ValidationError("Prompt cannot be empty")
    
    if len(prompt) > 1000:
        raise ValidationError("Prompt exceeds maximum length of 1000 characters")
    
    return sanitize_string(prompt, max_length=1000)


def validate_api_key_format(api_key: str) -> bool:
    """Validate API key format (not verification, just format check)"""
    if not api_key:
        return False
    return bool(API_KEY_PATTERN.match(api_key))


async def validate_image_upload(file: UploadFile) -> bytes:
    """
    Comprehensive image upload validation:
    - File size
    - MIME type verification
    - Magic bytes verification
    - Image integrity check
    """
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Reset file pointer for later use
    await file.seek(0)
    
    # 1. Check file size
    if file_size > MAX_IMAGE_SIZE:
        raise ValidationError(f"File size ({file_size} bytes) exceeds maximum allowed size ({MAX_IMAGE_SIZE} bytes)")
    
    if file_size == 0:
        raise ValidationError("File is empty")
    
    # 2. Verify MIME type using magic bytes
    mime = magic.from_buffer(content, mime=True)
    if mime not in ALLOWED_IMAGE_TYPES:
        raise ValidationError(f"Invalid file type: {mime}. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}")
    
    # 3. Verify it's actually a valid image by trying to open it
    try:
        img = Image.open(io.BytesIO(content))
        img.verify()  # Verify it's a valid image
        
        # Check dimensions (prevent extremely large images)
        img = Image.open(io.BytesIO(content))  # Re-open after verify
        width, height = img.size
        if width > 10000 or height > 10000:
            raise ValidationError(f"Image dimensions ({width}x{height}) are too large")
        
        if width < 10 or height < 10:
            raise ValidationError(f"Image dimensions ({width}x{height}) are too small")
        
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Invalid or corrupted image file: {str(e)}")
    
    return content


def validate_plan_name(plan_name: str) -> bool:
    """Validate plan name"""
    allowed_plans = ["starter", "growth", "scale"]
    return plan_name.lower() in allowed_plans


def validate_user_input(data: dict, required_fields: List[str]) -> dict:
    """
    Validate user registration/login input
    """
    validated = {}
    
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValidationError(f"Missing required field: {field}")
    
    # Validate email
    if 'email' in data:
        if not validate_email(data['email']):
            raise ValidationError("Invalid email format")
        validated['email'] = data['email'].lower().strip()
    
    # Validate password
    if 'password' in data:
        password = data['password']
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        if len(password) > 128:
            raise ValidationError("Password is too long")
        validated['password'] = password
    
    # Validate full name
    if 'fullName' in data:
        validated['fullName'] = sanitize_string(data['fullName'], max_length=100)
    
    return validated


def validate_key_type(key_type: str) -> bool:
    """Validate API key type"""
    return key_type in ['resize', 'create']
