import io
import sys
import os
import json
from PIL import Image
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

# Add current directory to path so we can import main
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from main import app, get_current_user

client = TestClient(app)

# Standard presets to test
VALID_PRESETS = [
    "16:9", "9:16", "1:1", "3:4", "21:9",
    "landscape", "story", "square", "portrait", "ultrawide"
]

# Non-standard presets that should be rejected
INVALID_PRESETS = [
    "1120x360", "2072x252", "1500x300", "5000x5000", "4:3", "3:2"
]

# Mock User Data
MOCK_USER = {
    "_id": "60c5f8b8f1a4c2b1a2b3c4d5",
    "email": "test@example.com",
    "engine_data": {
        "transformation": {
            "credits": {"remaining_units": 1000.0}
        }
    }
}

def mock_get_current_user():
    return MOCK_USER

def run_tests():
    # Override authentication
    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    # Create a dummy image for testing
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    results = []
    
    # Mocks for external dependencies
    with patch("main.client") as mock_gemini_client, \
         patch("main.s3_client") as mock_s3_client, \
         patch("main.consume_units") as mock_consume, \
         patch("main.log_usage") as mock_log:
        
        mock_log.return_value = "mock_log_id"
        
        # Configure Gemini Mock
        mock_response = MagicMock()
        mock_part = MagicMock()
        mock_part.inline_data.data = img_byte_arr
        mock_response.parts = [mock_part]
        mock_gemini_client.models.generate_content.return_value = mock_response
        
        # Configure S3 Mock
        mock_s3_client.put_object.return_value = {}
        mock_consume.return_value = True

        print(f"{'Aspect Ratio':<15} | {'Expected':<8} | {'Status':<10} | {'Message'}")
        print("-" * 70)

        # Test valid presets (should return 200)
        for preset in VALID_PRESETS:
            try:
                response = client.post(
                    "/api/resize",
                    data={
                        "aspect_ratio": preset,
                        "engine_type": "transformation"
                    },
                    files={"file": ("test.png", img_byte_arr, "image/png")}
                )
                
                status_code = response.status_code
                status = "SUCCESS" if status_code == 200 else "FAILED"
                msg = response.json().get("detail", "OK") if status == "FAILED" else "Successfully resized"
                
                results.append({
                    "aspect_ratio": preset,
                    "expected": "SUCCESS",
                    "status": status,
                    "status_code": status_code,
                    "message": msg
                })
                print(f"{preset:<15} | SUCCESS  | {status:<10} | {msg}")
                assert status_code == 200, f"Expected 200 for {preset}, got {status_code}"
            except Exception as e:
                results.append({
                    "aspect_ratio": preset,
                    "expected": "SUCCESS",
                    "status": "ERROR",
                    "message": str(e)
                })
                print(f"{preset:<15} | SUCCESS  | ERROR      | {str(e)}")

        # Test invalid presets (should return 400)
        for preset in INVALID_PRESETS:
            try:
                response = client.post(
                    "/api/resize",
                    data={
                        "aspect_ratio": preset,
                        "engine_type": "transformation"
                    },
                    files={"file": ("test.png", img_byte_arr, "image/png")}
                )
                
                status_code = response.status_code
                status = "SUCCESS" if status_code == 400 else "FAILED"
                msg = response.json().get("detail", "OK")
                
                results.append({
                    "aspect_ratio": preset,
                    "expected": "REJECTED",
                    "status": status,
                    "status_code": status_code,
                    "message": msg
                })
                print(f"{preset:<15} | REJECTED | {status:<10} | {msg}")
                assert status_code == 400, f"Expected 400 for {preset}, got {status_code}"
            except Exception as e:
                results.append({
                    "aspect_ratio": preset,
                    "expected": "REJECTED",
                    "status": "ERROR",
                    "message": str(e)
                })
                print(f"{preset:<15} | REJECTED | ERROR      | {str(e)}")

    # Clear overrides
    app.dependency_overrides = {}
    
    # Save results to a file
    with open("resolution_test_results_v2.json", "w") as f:
        json.dump(results, f, indent=4)
    
    print("\nTests complete. Detailed results saved to resolution_test_results_v2.json")
    return results

if __name__ == "__main__":
    run_tests()
