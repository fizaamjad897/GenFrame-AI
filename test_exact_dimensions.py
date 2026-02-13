import io
import os
import sys
import requests
from PIL import Image

def test_exact_dimensions_via_api(email="muhammadhamzafaisal146@gmail.com"):
    """Test exact dimensions by calling the actual /api/resize endpoint."""
    print("=" * 70)
    print("TESTING EXACT DIMENSION OUTPUT VIA API")
    print("=" * 70)
    
    # Priority resolutions to test
    test_resolutions = [
        ("288:608", "Story/Reel Portrait"),
        ("324:828", "Skyline/Tall Portrait"),
        ("432:864", "Story/Reel Portrait"),
        ("396:576", "Portrait"),
        ("576:396", "Landscape"),
        ("624:336", "Landscape")
    ]
    
    API_URL = "http://localhost:8000/api/resize"
    
    # Get auth token (you'll need to provide this)
    print("\n⚠️ NOTE: This test requires the backend server to be running on localhost:8000")
    print("⚠️ NOTE: You need to provide a valid auth token\n")
    
    token = input("Enter your auth token (or press Enter to skip): ").strip()
    if not token:
        print("❌ No token provided. Exiting.")
        return
    
    # Create test image
    print("🖼️ Creating test image (100x100 blue)...")
    test_img = Image.new('RGB', (100, 100), color='blue')
    img_bytes = io.BytesIO()
    test_img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    results = []
    
    for aspect_ratio, description in test_resolutions:
        print(f"\n{'='*70}")
        print(f"Testing: {aspect_ratio} ({description})")
        print(f"{'='*70}")
        
        try:
            # Parse expected dimensions
            w, h = map(int, aspect_ratio.split(':'))
            print(f"📐 Expected output: {w}x{h}")
            
            # Prepare request
            files = {'file': ('test.png', img_bytes.getvalue(), 'image/png')}
            data = {
                'aspect_ratio': aspect_ratio,
                'engine_type': 'transformation'
            }
            headers = {'Authorization': f'Bearer {token}'}
            
            print(f"📡 Calling API...")
            response = requests.post(API_URL, files=files, data=data, headers=headers)
            
            if not response.ok:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                results.append({
                    "ratio": aspect_ratio,
                    "status": "API_ERROR",
                    "reason": f"{response.status_code}: {response.text[:100]}"
                })
                continue
            
            # Get the image URL from response
            response_data = response.json()
            image_url = response_data.get('url')
            
            if not image_url:
                print(f"❌ No image URL in response")
                results.append({
                    "ratio": aspect_ratio,
                    "status": "NO_URL"
                })
                continue
            
            # Download and check dimensions
            print(f"📥 Downloading image from: {image_url[:50]}...")
            img_response = requests.get(image_url)
            generated = Image.open(io.BytesIO(img_response.content))
            final_w, final_h = generated.size
            
            print(f"✅ Final output: {final_w}x{final_h}")
            
            # Verify exact match
            if final_w == w and final_h == h:
                print(f"🎉 SUCCESS: Exact dimensions achieved!")
                results.append({
                    "ratio": aspect_ratio,
                    "expected": f"{w}x{h}",
                    "actual": f"{final_w}x{final_h}",
                    "status": "PASS"
                })
            else:
                print(f"❌ FAIL: Dimensions don't match")
                results.append({
                    "ratio": aspect_ratio,
                    "expected": f"{w}x{h}",
                    "actual": f"{final_w}x{final_h}",
                    "status": "FAIL"
                })
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append({
                "ratio": aspect_ratio,
                "status": "ERROR",
                "reason": str(e)
            })
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    passed = sum(1 for r in results if r.get("status") == "PASS")
    total = len(results)
    print(f"\nPassed: {passed}/{total}")
    
    for result in results:
        status_icon = "✅" if result.get("status") == "PASS" else "❌"
        print(f"{status_icon} {result['ratio']}: {result.get('status')}")
        if result.get("expected"):
            print(f"   Expected: {result['expected']}, Got: {result['actual']}")

if __name__ == "__main__":
    test_exact_dimensions_via_api()
