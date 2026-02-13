import io
import sys
import os
import uuid
import json
from datetime import datetime
from PIL import Image
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

# Add current directory to path so we can import main
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from main import app, get_current_user

client = TestClient(app)

# Original Resolutions to test
RESOLUTIONS = [
    "1120x360", "1152x288", "1152x384", "1188x288", "1368x324", "1376x288", "1764x468",
    "288x608", "288x648", "324x828", "396x576", "416x480", "416x576", "416x800",
    "432x864", "468x756", "504x864", "512x1280", "570x600", "576x396", "608x288",
    "624x336", "794x396", "800x416", "864x432", "900x288", "928x288"
]

# Stress Test Resolutions (> 4:1 and other extremes)
STRESS_TESTS = [
    "1500x300",  # 5:1
    "3000x300",  # 10:1
    "6000x300",  # 20:1
    "300x1500",  # 1:5
    "300x3000",  # 1:10
    "300x6000",  # 1:20
    "5000x5000"  # Large Square
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

    all_tests = [(r, "NORMAL") for r in RESOLUTIONS] + [(r, "STRESS") for r in STRESS_TESTS]
    results = []
    
    # Mocks for external dependencies
    with patch("main.client") as mock_gemini_client, \
         patch("main.s3_client") as mock_s3_client, \
         patch("main.consume_units") as mock_consume, \
         patch("main.log_usage") as mock_log:
        
        # Configure Gemini Mock
        mock_response = MagicMock()
        mock_part = MagicMock()
        mock_part.inline_data.data = img_byte_arr
        mock_response.parts = [mock_part]
        mock_gemini_client.models.generate_content.return_value = mock_response
        
        # Configure S3 Mock
        mock_s3_client.put_object.return_value = {}

        print(f"{'Resolution':<12} | {'Ratio':<10} | {'Type':<8} | {'Status':<10} | {'Message'}")
        print("-" * 70)

        for res, test_type in all_tests:
            try:
                # Basic cleaning of input
                clean_res = res.replace('х', 'x').strip() 
                width, height = map(int, clean_res.split('x'))
                ratio_val = width / height
                aspect_ratio = f"{width}:{height}"
                
                # Make the request
                response = client.post(
                    "/api/resize",
                    data={
                        "aspect_ratio": aspect_ratio,
                        "engine_type": "transformation"
                    },
                    files={"file": ("test.png", img_byte_arr, "image/png")}
                )
                
                status = "SUCCESS" if response.status_code == 200 else "FAILED"
                msg = response.json().get("detail", "OK") if status == "FAILED" else f"Ratio: {ratio_val:.2f}:1"
                
                results.append({
                    "resolution": res,
                    "aspect_ratio": aspect_ratio,
                    "ratio_decimal": round(ratio_val, 2),
                    "type": test_type,
                    "status": status,
                    "message": msg
                })
                
                print(f"{res:<12} | {ratio_val:>9.2f} | {test_type:<8} | {status:<10} | {msg}")
                
            except Exception as e:
                results.append({
                    "resolution": res,
                    "type": test_type,
                    "status": "ERROR",
                    "message": str(e)
                })
                print(f"{res:<12} | {'N/A':<10} | {test_type:<8} | {'ERROR':<10} | {str(e)}")

    # Clear overrides
    app.dependency_overrides = {}
    
    # Save results to a file for the user
    with open("resolution_test_results_v2.json", "w") as f:
        json.dump(results, f, indent=4)
    
    print("\nTests complete. Detailed results saved to resolution_test_results_v2.json")
    return results

if __name__ == "__main__":
    run_tests()
