import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timedelta
import uuid
from models import User, UserRegister, UserLogin, ForgotPasswordRequest, ResetPasswordRequest
from passlib.context import CryptContext
from jose import JWTError, jwt
import smtplib
import bcrypt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT
# Use JWT_SECRET to avoid conflict with Digital Ocean SECRET_KEY
JWT_SECRET = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
SECRET_KEY = JWT_SECRET.strip("'\" ")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # Extend to 1 week for better UX during development

# MongoDB
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "visual_engine")

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your-email@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your-app-password")

# Initialize MongoDB
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017").strip("'\" ")
DB_NAME = os.getenv("DB_NAME", "visual_engine").strip("'\" ")

def get_db_client(url, max_retries=3):
    import time
    for i in range(max_retries):
        try:
            client = MongoClient(url, serverSelectionTimeoutMS=5000)
            # Force a command to verify connection
            client.admin.command('ping')
            return client
        except Exception as e:
            if i < max_retries - 1:
                print(f"Connection attempt {i+1} failed ({e}). Retrying in 2 seconds...")
                time.sleep(2)
            else:
                print(f"Failed to connect to MongoDB after {max_retries} attempts: {e}")
                raise

try:
    client = get_db_client(MONGODB_URL)
    db = client[DB_NAME]
    users_collection = db["users"]
    password_resets_collection = db["password_resets"]
    plans_collection = db["plans"]
    usage_logs_collection = db["usage_logs"]
    billing_records_collection = db["billing_records"]
    print("Connected to MongoDB successfully")
except Exception as e:
    # If the ping fails, we still might want to proceed if it's a transient DNS issue 
    # but the MongoClient object itself is likely broken for SRV records if it failed here.
    raise

# Create indexes
users_collection.create_index("email", unique=True)
password_resets_collection.create_index("createdAt", expireAfterSeconds=3600)  # Expire after 1 hour
usage_logs_collection.create_index("userId")
usage_logs_collection.create_index("timestamp")
billing_records_collection.create_index("userId")
billing_records_collection.create_index("billingPeriodStart")

# Utility functions
def hash_password(password: str) -> str:
    # Use bcrypt directly to avoid passlib compatibility issues with newer bcrypt versions
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Use bcrypt directly to avoid passlib compatibility issues with newer bcrypt versions
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def create_access_token(user_id: str, expires_delta: timedelta = None):
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.utcnow() + expires_delta
    to_encode = {"sub": user_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None

def get_user_by_email(email: str):
    user = users_collection.find_one({"email": email})
    return user

def get_user_by_id(user_id: str):
    from bson import ObjectId
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        return user
    except:
        return None

def create_user(user_data: UserRegister):
    from bson import ObjectId
    
    # Check if user already exists
    existing_user = get_user_by_email(user_data.email)
    if existing_user:
        return None
    
    user_doc = {
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "fullName": user_data.fullName or "",
        "fingerprint": user_data.fingerprint,
        "presentationId": user_data.presentationId,
        "plan": "",
        "units": 0,
        "maxUnits": 0,  # Default: No free credits
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
    }
    
    result = users_collection.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    return user_doc

def verify_user_credentials(email: str, password: str):
    user = get_user_by_email(email)
    if not user:
        return None
    
    if not verify_password(password, user["password"]):
        return None
    
    return user

def increment_user_units(user_id: str):
    from bson import ObjectId
    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$inc": {"units": 1}, "$set": {"updatedAt": datetime.utcnow()}}
    )
    return result.modified_count > 0

def update_user_plan(user_id: str, plan: str, max_units: int):
    from bson import ObjectId
    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"plan": plan, "maxUnits": max_units, "units": 0, "updatedAt": datetime.utcnow()}}
    )
    return result.modified_count > 0

def reset_user_units(user_id: str):
    from bson import ObjectId
    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"units": 0, "updatedAt": datetime.utcnow()}}
    )
    return result.modified_count > 0

def create_password_reset_token(email: str) -> str:
    token = str(uuid.uuid4())
    password_resets_collection.insert_one({
        "email": email,
        "token": token,
        "createdAt": datetime.utcnow(),
    })
    return token

def verify_password_reset_token(token: str):
    reset_doc = password_resets_collection.find_one({"token": token})
    return reset_doc

def reset_password_by_token(token: str, new_password: str):
    reset_doc = verify_password_reset_token(token)
    if not reset_doc:
        return False
    
    email = reset_doc["email"]
    user = get_user_by_email(email)
    if not user:
        return False
    
    from bson import ObjectId
    users_collection.update_one(
        {"_id": ObjectId(user["_id"])},
        {"$set": {"password": hash_password(new_password), "updatedAt": datetime.utcnow()}}
    )
    
    password_resets_collection.delete_one({"token": token})
    return True

def send_password_reset_email(email: str, reset_token: str):
    """Send password reset email - returns token for development mode"""
    # Check if we're in development mode (no valid email credentials)
    is_dev_mode = (
        not SENDER_EMAIL or SENDER_EMAIL == "your-email@gmail.com" or
        not SENDER_PASSWORD or SENDER_PASSWORD == "your-app-password"
    )
    
    if is_dev_mode:
        print(f"[DEV MODE] Password reset token for {email}: {reset_token}")
        return True, reset_token  # Return token for testing
    
    try:
        reset_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/auth?form=reset&token={reset_token}"
        
        message = MIMEMultipart("alternative")
        message["Subject"] = "Password Reset Request"
        message["From"] = SENDER_EMAIL
        message["To"] = email
        
        html = f"""\
        <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>You have requested to reset your password. Click the link below to proceed:</p>
                <a href="{reset_link}">Reset Password</a>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this, please ignore this email.</p>
            </body>
        </html>
        """
        
        part = MIMEText(html, "html")
        message.attach(part)
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, email, message.as_string())
        
        print(f"Password reset email sent to {email}")
        return True, None
    except Exception as e:
        print(f"Error sending email to {email}: {e}")
        print(f"Reset token (for manual testing): {reset_token}")
        return False, reset_token  # Return token even if email fails

def user_doc_to_response(user_doc):
    """Convert MongoDB user document to response format"""
    return {
        "id": str(user_doc["_id"]),
        "email": user_doc["email"],
        "fullName": user_doc.get("fullName", ""),
        "avatar": user_doc.get("avatar"),
        "plan": user_doc.get("plan", ""),
        "units": user_doc.get("units", 0),
        "maxUnits": user_doc.get("maxUnits", 0),
        "createdAt": user_doc.get("createdAt"),
    }

def log_usage(user_id: str, operation: str, aspect_ratio: str, success: bool, image_url: str = None):
    """Log a usage operation for billing purposes"""
    usage_doc = {
        "userId": user_id,
        "operation": operation,
        "aspectRatio": aspect_ratio,
        "timestamp": datetime.utcnow(),
        "success": success,
        "imageUrl": image_url
    }
    usage_logs_collection.insert_one(usage_doc)
    return True

def get_user_usage_stats(user_id: str):
    """Get usage statistics for a user"""
    from bson import ObjectId
    user = get_user_by_id(user_id)
    if not user:
        return None
    
    # Get current billing period usage
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    usage_count = usage_logs_collection.count_documents({
        "userId": user_id,
        "timestamp": {"$gte": current_month_start},
        "success": True
    })
    
    return {
        "userId": user_id,
        "plan": user.get("plan") or "free tier",
        "unitsUsed": user.get("units", 0),
        "maxUnits": user.get("maxUnits", 0),
        "remainingUnits": user.get("maxUnits", 0) - user.get("units", 0),
        "overageUnits": max(0, user.get("units", 0) - user.get("maxUnits", 0)),
        "currentMonthOperations": usage_count
    }

def calculate_overage_charge(units_used: int, max_units: int, overage_rate: float = 0.19):
    """Calculate overage charges"""
    if units_used <= max_units:
        return 0.0
    overage_units = units_used - max_units
    return round(overage_units * overage_rate, 2)

def generate_monthly_bill(user_id: str):
    """Generate a monthly bill for a user"""
    from bson import ObjectId
    user = get_user_by_id(user_id)
    if not user:
        return None
    
    # Get plan details
    plan_name = user.get("plan", "")
    if not plan_name:
        # For users with no plan, we can use a free tier logic or return empty
        return None
    plan = plans_collection.find_one({"name": plan_name.capitalize()})
    if not plan:
        return None
    
    # Calculate billing period (current month)
    now = datetime.utcnow()
    period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # Get last day of current month
    if now.month == 12:
        period_end = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        period_end = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    units_used = user.get("units", 0)
    max_units = user.get("maxUnits", 0)
    overage_units = max(0, units_used - max_units)
    overage_charge = calculate_overage_charge(units_used, max_units)
    
    base_price = plan["price"]
    total_amount = base_price + overage_charge
    
    bill_doc = {
        "userId": user_id,
        "billingPeriodStart": period_start,
        "billingPeriodEnd": period_end,
        "plan": plan_name,
        "basePrice": base_price,
        "includedUnits": max_units,
        "unitsUsed": units_used,
        "overageUnits": overage_units,
        "overageCharge": overage_charge,
        "totalAmount": total_amount,
        "generatedAt": datetime.utcnow(),
        "status": "pending"
    }
    
    result = billing_records_collection.insert_one(bill_doc)
    bill_doc["_id"] = result.inserted_id
    return bill_doc

def get_billing_history(user_id: str, limit: int = 10):
    """Get billing history for a user"""
    bills = list(billing_records_collection.find(
        {"userId": user_id}
    ).sort("billingPeriodStart", -1).limit(limit))
    
    return bills

def get_all_plans():
    """Get all active pricing plans"""
    plans = list(plans_collection.find({"isActive": True}))
    return plans
