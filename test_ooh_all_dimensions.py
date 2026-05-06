"""
test_ooh_all_dimensions.py — Test OOH pipeline with all dimensions + caching

Tests:
1. Load a sample image
2. Transform to ALL OOH dimensions
3. Verify cache reuse (same image, different dimensions)
4. Show timing + cache hit/miss stats
"""

import asyncio
import sys
import time
from pathlib import Path
from PIL import Image
import io

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ooh_pipeline import ooh_resize

# ── OOH Media Dimensions ──────────────────────────────────────────────────────
OOH_DIMENSIONS = {
    "OOH_504X1008":  (504,   1008),   # Portrait extreme
    "OOH_792X216":   (792,   216),    # Landscape extreme thin
    "OOH_1060X360":  (1060,  360),    # Landscape wide
    "OOH_1232X672":  (1232,  672),    # Landscape moderate
    "OOH_1344X432":  (1344,  432),    # Landscape wide
    "OOH_1836X432":  (1836,  432),    # Landscape ultra-wide
    "OOH_1952X896":  (1952,  896),    # Landscape ultra-wide
    "OOH_2072X252":  (2072,  252),    # Landscape extreme thin
    "OOH_3924X972":  (3924,  972),    # Landscape ultra-wide
    "OOH_768X1152":  (768,   1152),   # Portrait moderate
    "OOH_800X400":   (800,   400),    # Landscape moderate
    "OOH_840X360":   (840,   360),    # Landscape moderate
    "OOH_960X576":   (960,   576),    # Landscape moderate
    "OOH_1024X320":  (1024,  320),    # Landscape wide
    "OOH_1280X384":  (1280,  384),    # Landscape wide
}


def create_test_image(width: int = 1200, height: int = 800) -> bytes:
    """Create a test image with various elements (text, shapes, colors)."""
    img = Image.new("RGB", (width, height), color=(240, 240, 240))
    pixels = img.load()
    
    # Add some colored rectangles (simulate components)
    # Red rectangle (top-left)
    for x in range(50, 350):
        for y in range(50, 250):
            pixels[x, y] = (220, 50, 50)
    
    # Blue rectangle (top-right)
    for x in range(width - 300, width - 50):
        for y in range(50, 250):
            pixels[x, y] = (50, 50, 220)
    
    # Green rectangle (center)
    for x in range(width // 2 - 150, width // 2 + 150):
        for y in range(height // 2 - 100, height // 2 + 100):
            pixels[x, y] = (50, 220, 50)
    
    # Yellow rectangle (bottom)
    for x in range(100, width - 100):
        for y in range(height - 150, height - 50):
            pixels[x, y] = (220, 220, 50)
    
    # Convert to bytes
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


async def test_single_dimension(
    image_bytes: bytes,
    name: str,
    width: int,
    height: int,
    output_dir: Path,
) -> dict:
    """Test resizing to a single dimension and measure time."""
    start = time.time()
    try:
        result = await ooh_resize(image_bytes, width, height)
        elapsed = time.time() - start
        
        if result:
            # Save the result
            output_path = output_dir / f"{name}_{width}x{height}.png"
            output_path.write_bytes(result)
            return {
                "name": name,
                "dims": f"{width}×{height}",
                "status": "✅ SUCCESS",
                "time": f"{elapsed:.2f}s",
                "size": f"{len(result) / 1024:.1f}KB",
                "output": str(output_path),
            }
        else:
            return {
                "name": name,
                "dims": f"{width}×{height}",
                "status": "❌ FAILED",
                "time": f"{time.time() - start:.2f}s",
                "error": "Returned None",
            }
    except Exception as e:
        return {
            "name": name,
            "dims": f"{width}×{height}",
            "status": "❌ ERROR",
            "time": f"{time.time() - start:.2f}s",
            "error": str(e)[:100],
        }


async def main():
    print("=" * 80)
    print("OOH Pipeline — All Dimensions Test + Cache Verification")
    print("=" * 80)
    
    # Create output directory
    output_dir = Path(__file__).parent / "ooh_test_outputs"
    output_dir.mkdir(exist_ok=True)
    print(f"\n📁 Output directory: {output_dir}")
    
    # Create test image (1200×800, has multiple colored regions = multiple components)
    print("\n📷 Creating test image (1200×800)...")
    image_bytes = create_test_image(1200, 800)
    print(f"   Image size: {len(image_bytes) / 1024:.1f}KB")
    
    # Test all dimensions
    print(f"\n⏳ Testing {len(OOH_DIMENSIONS)} OOH dimensions...")
    print("   (First dimension = decomposition + cache write)")
    print("   (Remaining = cache hit, fast recomposition)\n")
    
    results = []
    total_start = time.time()
    
    for idx, (name, (width, height)) in enumerate(OOH_DIMENSIONS.items(), 1):
        print(f"   [{idx:02d}/{len(OOH_DIMENSIONS)}] {name:20s} ({width:4d}×{height:4d})...", end=" ", flush=True)
        
        result = await test_single_dimension(
            image_bytes,
            name,
            width,
            height,
            output_dir,
        )
        results.append(result)
        
        status_icon = "✅" if "SUCCESS" in result["status"] else "❌"
        print(f"{status_icon} {result['time']:>8s}", flush=True)
    
    total_time = time.time() - total_start
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    successful = [r for r in results if "SUCCESS" in r["status"]]
    failed = [r for r in results if "SUCCESS" not in r["status"]]
    
    print(f"\n✅ Successful: {len(successful)}/{len(OOH_DIMENSIONS)}")
    print(f"❌ Failed: {len(failed)}/{len(OOH_DIMENSIONS)}")
    print(f"⏱️  Total time: {total_time:.2f}s")
    
    if failed:
        print("\n❌ Failed Dimensions:")
        for r in failed:
            print(f"   • {r['name']:20s} ({r['dims']:15s}): {r.get('error', r['status'])}")
    
    print("\n✅ Successful Dimensions:")
    for r in successful:
        print(f"   • {r['name']:20s} ({r['dims']:15s}): {r['time']:>8s}  {r['size']:>10s}")
    
    # Cache info
    cache_root = Path(__file__).parent / "ooh_decomposition_cache"
    if cache_root.exists():
        cache_entries = list(cache_root.glob("*"))
        print(f"\n💾 Cache Directory: {cache_root}")
        print(f"   Cached decompositions: {len(cache_entries)}")
        total_cache_size = sum(f.stat().st_size for f in cache_root.glob("*/*") if f.is_file())
        print(f"   Total cache size: {total_cache_size / 1024 / 1024:.1f}MB")
    
    print("\n" + "=" * 80)
    print(f"📊 Test complete! Outputs saved to: {output_dir}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
