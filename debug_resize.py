import io
import os
import sys
import json
import uuid
from datetime import datetime
from PIL import Image

# Add current directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_internal_logic(aspect_ratio="1:1", email="muhammadhamzafaisal146@gmail.com"):
    """Test the internal logic of main.py without HTTP but with real API calls."""
    print(f"🧪 --- DEBUG START: {aspect_ratio} ---")
    
    try:
        print("📥 Importing main.py...")
        import importlib
        import main
        importlib.reload(main)  # Force reload to get latest changes
        from main import client, s3_client, DO_SPACES_BUCKET_NAME, types
        print("✅ main.py imported successfully.")
        
        # Check authentication module findings
        print(f"🔍 Looking for user: {email}")
        user = main.auth_module.users_collection.find_one({"email": email})
        if not user:
            print(f"❌ User {email} not found in database.")
            return

        # Create dummy image
        print("🖼️ Creating test image (100x100 green)...")
        img = Image.new('RGB', (100, 100), color='green')
        
        # Gemini Call
        print(f"📡 Calling Gemini (Model: gemini-3-pro-image-preview, Ratio: {aspect_ratio})...")
        use_prompt = f"recreate this image in {aspect_ratio} ratio format"
        
        try:
            response = client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=[use_prompt, img],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio
                    )
                )
            )
            print("✅ Gemini API Call Success!")
        except Exception as gemini_err:
            print(f"❌ GEMINI ERROR: {gemini_err}")
            return

        # Extract Image Data
        image_data = None
        if response.parts:
            for part in response.parts:
                if part.inline_data:
                    image_data = part.inline_data.data
                    print(f"🖼️ Extracted image: {len(image_data)} bytes")
                    break
        
        if not image_data:
            print("❌ Gemini returned SUCCESS but NO image data was found in the response parts.")
            print(f"Full response details: {response}")
            return

        # S3 Upload
        print(f"☁️ Uploading to S3 (Bucket: {DO_SPACES_BUCKET_NAME})...")
        filename = f"test_debug/debug_{uuid.uuid4().hex[:8]}.png"
        try:
            s3_client.put_object(
                Bucket=DO_SPACES_BUCKET_NAME,
                Key=filename,
                Body=image_data,
                ContentType='image/png',
                ACL='public-read'
            )
            print(f"✅ S3 Upload Success! Path: {filename}")
        except Exception as s3_err:
            print(f"❌ S3 UPLOAD ERROR: {s3_err}")
            return

        print(f"🎉 TEST COMPLETED SUCCESSFULLY for {aspect_ratio}")

    except Exception as e:
        print(f"❌ UNEXPECTED CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test a standard ratio and one of the failing ones
    target_email = "muhammadhamzafaisal146@gmail.com"
    test_internal_logic("1:1", target_email)
    print("\n" + "="*50 + "\n")
    test_internal_logic("432:864", target_email)
