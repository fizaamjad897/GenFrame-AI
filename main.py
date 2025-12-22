from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import Response, FileResponse
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
import io

load_dotenv()

app = FastAPI(title="Nano Banana Resizer (Gemini Powered)")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Gemini Client (lazy init or global if key is present)
# We will init inside the function or global if key exists.
client = None
if GOOGLE_API_KEY:
    client = genai.Client(api_key=GOOGLE_API_KEY)
else:
    print("Warning: GOOGLE_API_KEY not set in .env")

@app.post("/resize")
async def resize_image(
    file: UploadFile = File(...),
    aspect_ratio: str = Form(..., description="Target aspect ratio, e.g., '16:9', '1:1', '4:3'")
):
    """
    Endpoint to resize an image intelligently using Gemini 3 Pro (Nano Banana Pro).
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
        # User's example template:
        # "recreate this image in 16:9 ratio format and keep all the the information of image intact . you can rearrange the elements to ensure it is perfect."
        prompt = (
            f"recreate this image in {aspect_ratio} ratio format and keep all the the information of image intact . "
            "you can rearrange the elements to ensure it is perfect."
        )
        
        # 3. Call the AI Service
        # Using 'gemini-3-pro-image-preview' as per documentation for Nano Banana Pro equivalent features
        # If this model is not available to the key, user might need to change it to 'gemini-2.0-flash-exp' or similar.
        model_name = "gemini-3-pro-image-preview" 

        response = client.models.generate_content(
            model=model_name,
            contents=[prompt, pil_image],
            config=types.GenerateContentConfig(
                response_modalities=["Image"],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio
                )
            )
        )
        
        # 4. Return the result
        # Check for generated image in parts
        if response.parts:
            for part in response.parts:
                if part.inline_data:
                    return Response(content=part.inline_data.data, media_type="image/png")
                # Some versions of SDK might behave differently, but inline_data.data is standard for 'Image' modality response in new SDK.

        # If we reach here, something might be off
        print(f"Full Response: {response}")
        raise HTTPException(status_code=500, detail="No image content returned from API.")
                
    except Exception as e:
        print(f"Error processing request: {e}")
        # In production, be careful about exposing raw error details
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@app.get("/")
async def read_root():
    return FileResponse('index.html')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
