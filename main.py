from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Header
from fastapi.responses import Response, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
import io
from datetime import datetime
import uuid
import boto3
from botocore.config import Config
from models import UserRegister, UserLogin, ForgotPasswordRequest, ResetPasswordRequest, TokenResponse, UserResponse, PlanUpgradeRequest
from auth import (
    create_user, verify_user_credentials, create_access_token, 
    verify_token, get_user_by_id, increment_user_units, 
    create_password_reset_token, reset_password_by_token, 
    send_password_reset_email, user_doc_to_response,
    get_all_plans, get_user_usage_stats, get_billing_history,
    generate_monthly_bill, log_usage
)

load_dotenv()

app = FastAPI(title="Visual Engine (Gemini Powered)")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Digital Ocean Spaces Configuration (matching NestJS env variable names)
# We use specific DO_ prefixes to avoid shadowing conflicts in .env
DO_SPACES_ACCESS_KEY = (os.getenv("DO_ACCESS_KEY_ID") or os.getenv("ACCESS_KEY_ID", "")).strip("'\" ")
DO_SPACES_SECRET_KEY = (os.getenv("DO_SECRET_KEY") or os.getenv("SECRET_KEY", "")).strip("'\" ")
DO_SPACES_ENDPOINT = os.getenv("ENDPOINT", "").strip("'\" ")
DO_SPACES_BUCKET_NAME = os.getenv("SPACENAME", "").strip("'\" ")

# Dependency for authentication
def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.split(" ")[1]
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

# Initialize Gemini Client (lazy init or global if key is present)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# We will init inside the function or global if key exists.
client = None
if GOOGLE_API_KEY:
    client = genai.Client(api_key=GOOGLE_API_KEY)
else:
    print("Warning: GOOGLE_API_KEY not set in .env")

# Initialize Digital Ocean Spaces client (matching NestJS implementation exactly)
if not DO_SPACES_ENDPOINT or not DO_SPACES_BUCKET_NAME:
    raise ValueError("ENDPOINT and SPACENAME must be set in environment variables")

if not DO_SPACES_ACCESS_KEY or not DO_SPACES_SECRET_KEY:
    raise ValueError("ACCESS_KEY_ID and SECRET_KEY must be set in environment variables")

try:
    # Clean endpoint - remove protocol if present
    endpoint_clean = DO_SPACES_ENDPOINT.replace('https://', '').replace('http://', '').strip()
    
    # Extract region from endpoint (e.g., sfo3.digitaloceanspaces.com -> sfo3)
    region = endpoint_clean.split('.')[0] if '.' in endpoint_clean else 'nyc3'
    
    # Ensure endpoint has protocol for boto3
    endpoint_url = endpoint_clean if endpoint_clean.startswith('http') else f'https://{endpoint_clean}'
    
    s3_client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=DO_SPACES_ACCESS_KEY,
        aws_secret_access_key=DO_SPACES_SECRET_KEY,
        region_name=region,
        config=Config(
            signature_version='s3v4',
            s3={'addressing_style': 'virtual'} # Recommended for Digital Ocean
        )
    )
    print("Digital Ocean Spaces client initialized")
except Exception as e:
    print(f"Error: Failed to initialize Digital Ocean Spaces client: {e}")
    raise

@app.post("/api/users/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    """Register a new user"""
    new_user = create_user(user_data)
    if not new_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    access_token = create_access_token(str(new_user["_id"]))
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_doc_to_response(new_user)
    }

@app.post("/api/users/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login user"""
    user = verify_user_credentials(credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(str(user["_id"]))
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_doc_to_response(user)
    }

@app.post("/api/users/request-password-reset")
async def request_password_reset(request: ForgotPasswordRequest):
    """Request password reset"""
    from auth import get_user_by_email
    user = get_user_by_email(request.email)
    if not user:
        # For security, don't reveal if email exists
        return {"message": "If email exists, reset link has been sent"}
    
    reset_token = create_password_reset_token(request.email)
    email_sent, token = send_password_reset_email(request.email, reset_token)
    
    # For development mode, return the token so user can test without email
    response = {"message": "Password reset token created"}
    if token:  # Token returned means dev mode or email failed
        response["dev_token"] = token
        response["message"] += " (Dev Mode - use token below)"
    
    return response

@app.post("/api/users/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset password using token"""
    success = reset_password_by_token(request.token, request.newPassword)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    return {"message": "Password reset successfully"}

@app.get("api/users/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user info"""
    return user_doc_to_response(current_user)

    return {
        "message": f"Plan upgraded to {request.plan}",
        "user": user_doc_to_response(updated_user)
    }

@app.get("/api/plans")
async def get_plans():
    """Get all available pricing plans"""
    plans = get_all_plans()
    # Convert ObjectId to string for JSON serialization
    for plan in plans:
        plan["_id"] = str(plan["_id"])
    return plans

@app.get("/api/users/usage")
async def get_usage(current_user = Depends(get_current_user)):
    """Get usage stats for current user"""
    stats = get_user_usage_stats(str(current_user["_id"]))
    if not stats:
        raise HTTPException(status_code=404, detail="User not found")
    return stats

@app.get("/api/users/billing-history")
async def get_billing(current_user = Depends(get_current_user)):
    """Get billing history for current user"""
    history = get_billing_history(str(current_user["_id"]))
    for bill in history:
        bill["_id"] = str(bill["_id"])
    return history

@app.post("/api/billing/generate")
async def generate_bill(current_user = Depends(get_current_user)):
    """Manually generate a bill for the current period (for demo)"""
    bill = generate_monthly_bill(str(current_user["_id"]))
    if not bill:
        raise HTTPException(status_code=400, detail="Failed to generate bill")
    bill["_id"] = str(bill["_id"])
    return bill


@app.post("/api/resize", response_class=JSONResponse)
async def resize_image(
    file: UploadFile = File(...),
    aspect_ratio: str = Form(..., description="Target aspect ratio, e.g., '16:9', '1:1', '4:3'"),
    prompt: str = Form(None, description="Optional custom prompt for image editing. If not provided, uses default resizing prompt."),
    current_user = Depends(get_current_user)
):
    """
    Endpoint to resize or edit an image intelligently using Gemini 3 Pro (Nano Banana Pro).
    If a custom prompt is provided, it will be used for editing; otherwise, defaults to resizing with the specified aspect ratio.
    """
    global client
    
    # Check user's plan and hits
    user_id = str(current_user["_id"])
    current_units = current_user.get("units", 0)
    max_units = current_user.get("maxUnits", 0)
    
    if current_units >= max_units:
        raise HTTPException(
            status_code=429, 
            detail=f"You have reached your {current_user.get('plan', 'Free Tier')} limit of {max_units} units. Please upgrade your plan."
        )
    
    if not client:
        # Try reloading env if key was added later
        load_dotenv()
        GOOGLE_API_KEY_LATEST = os.getenv("GOOGLE_API_KEY")
        if GOOGLE_API_KEY_LATEST:
            client = genai.Client(api_key=GOOGLE_API_KEY_LATEST)
        else:
            raise HTTPException(status_code=500, detail="Server Configuration Error: API Key missing")

    try:
        # 1. Read the image
        image_bytes = await file.read()
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        # 2. Construct the structured prompt
        if prompt:
            use_prompt = prompt
        else:
            use_prompt = (
                f"recreate this image in {aspect_ratio} ratio format and keep all the the information of image intact . "
                "you can rearrange the elements to ensure it is perfect."
            )
        
        # 3. Call the AI Service
        # Using 'gemini-3-pro-image-preview' as per documentation for Nano Banana Pro equivalent features
        # If this model is not available to the key, user might need to change it to 'gemini-2.0-flash-exp' or similar.
        model_name = "gemini-3-pro-image-preview" 

        response = client.models.generate_content(
            model=model_name,
            contents=[use_prompt, pil_image],
            config=types.GenerateContentConfig(
                response_modalities=["Image"],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio
                )
            )
        )
        
        # 4. Extract the generated image
        image_data = None
        if response.parts:
            for part in response.parts:
                if part.inline_data:
                    image_data = part.inline_data.data
                    break
        
        if not image_data:
            print(f"Full Response: {response}")
            raise HTTPException(status_code=500, detail="No image content returned from API.")
        
        # 5. Upload to Digital Ocean Spaces (matching NestJS implementation exactly)
        uploaded_url = None
        image_name = None
        
        # Generate a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"resized_images/{timestamp}_{unique_id}.png"
        image_name = f"{timestamp}_{unique_id}.png"
        
        try:
            bucket_name = DO_SPACES_BUCKET_NAME
            
            # Upload to Digital Ocean Spaces (matching NestJS implementation)
            s3_client.put_object(
                Bucket=bucket_name,
                Key=filename,
                Body=image_data,
                ContentType='image/png',
                ACL='public-read'  # Make the image publicly accessible
            )
            
            # Construct the public URL (matching NestJS format: https://{bucketName}.{endpoint}/{fileName})
            # Clean endpoint for URL construction (remove protocol if present)
            endpoint_for_url = DO_SPACES_ENDPOINT.replace('https://', '').replace('http://', '').strip()
            uploaded_url = f"https://{bucket_name}.{endpoint_for_url}/{filename}"
            print(f"Image uploaded to Digital Ocean Spaces: {uploaded_url}")
        except Exception as upload_error:
            print(f"Error uploading to Digital Ocean Spaces: {upload_error}")
            raise HTTPException(
                status_code=500,
                detail=f"Image generated but failed to upload to storage: {str(upload_error)}"
            )
        
        # 6. Return JSON response with URL and name
        if not uploaded_url or not image_name:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate upload URL or image name"
            )
        
        response_data = {
            "url": uploaded_url,
            "name": image_name
        }
        print(f"Returning response: {response_data}")
        
        # Explicitly return JSONResponse to ensure proper serialization
        return JSONResponse(content=response_data, status_code=200)
                
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"Error processing request: {e}")
        import traceback
        traceback.print_exc()
        # In production, be careful about exposing raw error details
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")
    
    finally:
        # Always increment units for successful or attempted operations
        if current_user:
            user_id = str(current_user["_id"])
            increment_user_units(user_id)
            # Log usage for detailed tracking and billing
            # We use local variables from the try block if they exist
            img_url = locals().get('uploaded_url')
            is_success = img_url is not None
            log_usage(
                user_id=user_id,
                operation="resize",
                aspect_ratio=aspect_ratio,
                success=is_success,
                image_url=img_url
            )

@app.get("/")
async def read_root():
    return FileResponse('index.html')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
