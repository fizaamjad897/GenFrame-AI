from fastapi import FastAPI, File, UploadFile, Form, HTTPException
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

load_dotenv()

app = FastAPI(title="Nano Banana Resizer (Gemini Powered)")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Digital Ocean Spaces Configuration (matching NestJS env variable names)
DO_SPACES_ACCESS_KEY = os.getenv("ACCESS_KEY_ID", "").strip("'\"")
DO_SPACES_SECRET_KEY = os.getenv("SECRET_KEY", "").strip("'\"")
DO_SPACES_ENDPOINT = os.getenv("ENDPOINT", "").strip("'\"")
DO_SPACES_BUCKET_NAME = os.getenv("SPACENAME", "").strip("'\"")

# Initialize Gemini Client (lazy init or global if key is present)
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
        config=Config(signature_version='s3v4')
    )
    print("Digital Ocean Spaces client initialized")
except Exception as e:
    print(f"Error: Failed to initialize Digital Ocean Spaces client: {e}")
    raise

@app.post("/resize", response_class=JSONResponse)
async def resize_image(
    file: UploadFile = File(...),
    aspect_ratio: str = Form(..., description="Target aspect ratio, e.g., '16:9', '1:1', '4:3'"),
    prompt: str = Form(None, description="Optional custom prompt for image editing. If not provided, uses default resizing prompt.")
):
    """
    Endpoint to resize or edit an image intelligently using Gemini 3 Pro (Nano Banana Pro).
    If a custom prompt is provided, it will be used for editing; otherwise, defaults to resizing with the specified aspect ratio.
    """
    global client
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

@app.get("/")
async def read_root():
    return FileResponse('index.html')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
