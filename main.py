from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Header, Request, Query
from fastapi.responses import Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
import io
from datetime import datetime
from models import UserRegister, UserLogin, ForgotPasswordRequest, ResetPasswordRequest, TokenResponse, UserResponse, PlanUpgradeRequest
from auth import (
    create_user, verify_user_credentials, create_access_token, 
    verify_token, get_user_by_id, 
    create_password_reset_token, reset_password_by_token, 
    send_password_reset_email, user_doc_to_response,
    get_all_plans, get_user_usage_stats, get_billing_history,
    generate_monthly_bill, log_usage
)
import auth as auth_module

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



# Dependency for JWT auth (user management endpoints)
def get_current_user_jwt(authorization: str = Header(None)):
    """JWT authentication for user management endpoints only"""
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

# Dependency for API key auth (image processing endpoints)
def get_current_user_apikey(request: Request, x_api_key: str = Header(..., alias="X-API-KEY")):
    """API key authentication required for image processing endpoints"""
    user, key_type = auth_module.verify_api_key(x_api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Store key type in request state for endpoint verification
    request.state.key_type = key_type
    return user

# Initialize Gemini Client (lazy init or global if key is present)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# We will init inside the function or global if key exists.
client = None
if GOOGLE_API_KEY:
    client = genai.Client(api_key=GOOGLE_API_KEY)
else:
    print("Warning: GOOGLE_API_KEY not set in .env")



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

@app.get("/api/users/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user_jwt)):
    """Get current user info"""
    return user_doc_to_response(current_user)

@app.post("/api/users/api-key")
async def create_api_key_endpoint(
    type: str = Query(..., regex="^(resize|create)$"),
    current_user = Depends(get_current_user_jwt)
):
    """Create an API key for the authenticated user and specific type (resize/create)."""
    user_id = str(current_user["_id"])
    
    # Check if key exists for this type
    api_keys = current_user.get("api_keys", {})
    if type == "resize" and api_keys.get("resize_hash"):
         raise HTTPException(status_code=400, detail="Resize API key already exists. Delete it first.")
    if type == "create" and api_keys.get("create_hash"):
         raise HTTPException(status_code=400, detail="Create API key already exists. Delete it first.")
         
    raw_key = auth_module.generate_api_key_for_user(user_id, type)
    if not raw_key:
        raise HTTPException(status_code=500, detail="Failed to create API key")
    return {"api_key": raw_key, "type": type, "message": "Store this key securely. It will not be shown again."}

@app.delete("/api/users/api-key")
async def delete_api_key_endpoint(
    type: str = Query(..., regex="^(resize|create)$"),
    current_user = Depends(get_current_user_jwt)
):
    """Delete the active API key for the authenticated user and type."""
    user_id = str(current_user["_id"])
    success = auth_module.delete_api_key(user_id, type)
    if not success:
        raise HTTPException(status_code=400, detail=f"No {type} API key to delete")
    return {"message": f"{type} API key deleted"}

@app.get("/api/plans")
async def get_plans():
    """Get all available pricing plans"""
    plans = get_all_plans()
    # Convert ObjectId to string for JSON serialization
    for plan in plans:
        plan["_id"] = str(plan["_id"])
    return plans

@app.get("/api/users/usage")
async def get_usage(current_user = Depends(get_current_user_jwt)):
    """Get usage stats for current user"""
    stats = get_user_usage_stats(str(current_user["_id"]))
    if not stats:
        raise HTTPException(status_code=404, detail="User not found")
    return stats

@app.get("/api/users/billing-history")
async def get_billing(current_user = Depends(get_current_user_jwt)):
    """Get billing history for current user"""
    history = get_billing_history(str(current_user["_id"]))
    for bill in history:
        bill["_id"] = str(bill["_id"])
    return history

@app.post("/api/billing/generate")
async def generate_bill(current_user = Depends(get_current_user_jwt)):
    """Manually generate a bill for the current period (for demo)"""
    bill = generate_monthly_bill(str(current_user["_id"]))
    if not bill:
        raise HTTPException(status_code=400, detail="Failed to generate bill")
    bill["_id"] = str(bill["_id"])
    return bill


@app.post("/api/resize")
async def resize_image(
    request: Request,
    file: UploadFile = File(...),
    aspect_ratio: str = Form(..., description="Target aspect ratio, e.g., '16:9', '1:1', '4:3'"),
    current_user = Depends(get_current_user_apikey)
):
    """
    Endpoint to resize image.
    Requires 'resize' API Key (X-API-KEY header).
    Deducts 1 'resize' credit.
    Returns image bytes directly.
    """
    # 1. Scope Enforcement
    key_type = getattr(request.state, "key_type", None)
    if key_type != "resize":
         raise HTTPException(status_code=403, detail="Invalid API Key type for this endpoint. Use a 'resize' key.")

    global client
    
    # 2. Credit Check & Deduction
    user_id = str(current_user["_id"])
    if not auth_module.check_and_deduct_credits(user_id, "resize"):
        raise HTTPException(status_code=402, detail="Insufficient resize credits (monthly or addon).")

    # 3. Initialize Gemini
    if not client:
        load_dotenv()
        GOOGLE_API_KEY_LATEST = os.getenv("GOOGLE_API_KEY")
        if GOOGLE_API_KEY_LATEST:
            client = genai.Client(api_key=GOOGLE_API_KEY_LATEST)
        else:
            raise HTTPException(status_code=500, detail="Server Configuration Error: API Key missing")

    try:
        # 4. Process Request
        image_bytes = await file.read()
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        use_prompt = f"recreate this image in {aspect_ratio} ratio format and keep all the information intact."
        
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
        
        image_data = None
        if response.parts:
            for part in response.parts:
                if part.inline_data:
                    image_data = part.inline_data.data
                    break
        
        if not image_data:
            print(f"Full Response: {response}")
            raise HTTPException(status_code=500, detail="No image content returned from API.")
            
        # 5. Log Usage (without URL)
        log_usage(
            user_id=user_id,
            operation="resize",
            aspect_ratio=aspect_ratio,
            success=True,
            image_url="direct_download" 
        )
        
        # 6. Return Image Directly
        return Response(content=image_data, media_type="image/png")
                
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing request: {e}")
        # Log failure
        log_usage(user_id=str(current_user["_id"]), operation="resize", aspect_ratio=aspect_ratio, success=False, image_url=None)
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")


@app.post("/api/create")
async def create_image(
    request: Request,
    prompt: str = Form(..., description="Prompt to generate image."),
    aspect_ratio: str = Form(..., description="Target aspect ratio, e.g., '16:9', '1:1'"),
    file: UploadFile = File(None, description="Optional reference image."),
    current_user = Depends(get_current_user_apikey)
):
    """
    Endpoint to create new image from prompt (and optional reference).
    Requires 'create' API Key (X-API-KEY header).
    Deducts 1 'create' credit.
    Returns image bytes directly.
    """
    # 1. Scope Enforcement
    key_type = getattr(request.state, "key_type", None)
    if key_type != "create":
         raise HTTPException(status_code=403, detail="Invalid API Key type for this endpoint. Use a 'create' key.")

    global client
    
    # 2. Credit Check & Deduction
    user_id = str(current_user["_id"])
    if not auth_module.check_and_deduct_credits(user_id, "create"):
        raise HTTPException(status_code=402, detail="Insufficient create credits (monthly or addon).")

    # 3. Initialize Gemini
    if not client:
        load_dotenv()
        GOOGLE_API_KEY_LATEST = os.getenv("GOOGLE_API_KEY")
        if GOOGLE_API_KEY_LATEST:
            client = genai.Client(api_key=GOOGLE_API_KEY_LATEST)
        else:
            raise HTTPException(status_code=500, detail="Server Configuration Error: API Key missing")

    try:
        # 4. Prepare Contents
        contents = [prompt]
        if file:
            image_bytes = await file.read()
            pil_image = Image.open(io.BytesIO(image_bytes))
            contents.append(pil_image)
        
        model_name = "gemini-3-pro-image-preview" 

        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["Image"],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio
                )
            )
        )
        
        image_data = None
        if response.parts:
            for part in response.parts:
                if part.inline_data:
                    image_data = part.inline_data.data
                    break
        
        if not image_data:
            print(f"Full Response: {response}")
            raise HTTPException(status_code=500, detail="No image content returned from API.")
            
        # 5. Log Usage
        log_usage(
            user_id=user_id,
            operation="create",
            aspect_ratio=aspect_ratio,
            success=True,
            image_url="direct_download"
        )
        
        # 6. Return Image Directly
        return Response(content=image_data, media_type="image/png")
                
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing request: {e}")
        log_usage(user_id=str(current_user["_id"]), operation="create", aspect_ratio=aspect_ratio, success=False, image_url=None)
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@app.get("/")
async def read_root():
    return FileResponse('index.html')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
