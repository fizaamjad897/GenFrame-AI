"""
test_qms_all_dimensions.py — Test QMS pipeline with all dimensions + caching

Usage:
    python test_qms_all_dimensions.py --image /path/to/image.png
    python test_qms_all_dimensions.py --image https://example.com/image.jpg
"""

import argparse
import asyncio
import sys
import time
import urllib.request
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

sys.path.insert(0, str(Path(__file__).parent))

from ooh_pipeline import ooh_resize

# ── QMS Media Dimensions ──────────────────────────────────────────────────────
QMS_DIMENSIONS = {
    "QMS_2640X288":  (2640,  288),   # Ultra-extreme thin strip (9.2:1)
    "QMS_1824X432":  (1824,  432),   # Super wide billboard (4.2:1)
    "QMS_1728X432":  (1728,  432),   # Wide billboard (4:1)
    "QMS_1440X360":  (1440,  360),   # Wide billboard (4:1)
    "QMS_1120X320":  (1120,  320),   # Wide strip billboard (3.5:1)
    "QMS_760X240":   (760,   240),   # Wide strip (3.2:1)
    "QMS_1184X384":  (1184,  384),   # Wide billboard (3.1:1)
    "QMS_1472X480":  (1472,  480),   # Wide billboard (3.1:1)
    "QMS_1296X432":  (1296,  432),   # Wide billboard (3:1)
    "QMS_1200X400":  (1200,  400),   # Wide billboard (3:1)
    "QMS_1188X396":  (1188,  396),   # Wide billboard (3:1)
}


def load_image(source: str) -> bytes:
    """Load image bytes from a local path or URL."""
    if source.startswith("http://") or source.startswith("https://"):
        print(f"   Downloading from URL...")
        with urllib.request.urlopen(source) as resp:
            return resp.read()
    else:
        return Path(source).read_bytes()


async def test_single_dimension(
    image_bytes: bytes,
    name: str,
    width: int,
    height: int,
    output_dir: Path,
) -> dict:
    start = time.time()
    try:
        result = await ooh_resize(image_bytes, width, height)
        elapsed = time.time() - start

        if result:
            output_path = output_dir / f"{name}_{width}x{height}.png"
            output_path.write_bytes(result)
            return {
                "name": name,
                "dims": f"{width}×{height}",
                "status": "✅ SUCCESS",
                "time": f"{elapsed:.2f}s",
                "size": f"{len(result) / 1024:.1f}KB",
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
    parser = argparse.ArgumentParser(description="Test QMS pipeline across all dimensions")
    parser.add_argument("--image", required=True, help="Local path or URL to the source image")
    args = parser.parse_args()

    print("=" * 80)
    print("QMS Pipeline — All Dimensions Test + Cache Verification")
    print("=" * 80)

    output_dir = Path(__file__).parent / "qms_test_outputs"
    output_dir.mkdir(exist_ok=True)
    print(f"\n📁 Output directory: {output_dir}")

    print(f"\n📷 Loading image: {args.image}")
    image_bytes = load_image(args.image)
    print(f"   Image size: {len(image_bytes) / 1024:.1f}KB")

    print(f"\n⏳ Testing {len(QMS_DIMENSIONS)} QMS dimensions...")
    print("   (First dimension = decomposition + cache write)")
    print("   (Remaining = cache hit, fast recomposition)\n")

    results = []
    total_start = time.time()

    for idx, (name, (width, height)) in enumerate(QMS_DIMENSIONS.items(), 1):
        print(f"   [{idx:02d}/{len(QMS_DIMENSIONS)}] {name:20s} ({width:4d}×{height:4d})...", end=" ", flush=True)
        result = await test_single_dimension(image_bytes, name, width, height, output_dir)
        results.append(result)
        status_icon = "✅" if "SUCCESS" in result["status"] else "❌"
        print(f"{status_icon} {result['time']:>8s}", flush=True)

    total_time = time.time() - total_start

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    successful = [r for r in results if "SUCCESS" in r["status"]]
    failed = [r for r in results if "SUCCESS" not in r["status"]]

    print(f"\n✅ Successful: {len(successful)}/{len(QMS_DIMENSIONS)}")
    print(f"❌ Failed:     {len(failed)}/{len(QMS_DIMENSIONS)}")
    print(f"⏱️  Total time: {total_time:.2f}s")

    if failed:
        print("\n❌ Failed Dimensions:")
        for r in failed:
            print(f"   • {r['name']:20s} ({r['dims']:15s}): {r.get('error', r['status'])}")

    print("\n✅ Successful Dimensions:")
    for r in successful:
        print(f"   • {r['name']:20s} ({r['dims']:15s}): {r['time']:>8s}  {r['size']:>10s}")

    cache_root = Path(__file__).parent / "ooh_decomposition_cache"
    if cache_root.exists():
        cache_entries = list(cache_root.glob("*"))
        total_cache_size = sum(f.stat().st_size for f in cache_root.glob("*/*") if f.is_file())
        print(f"\n💾 Cache: {len(cache_entries)} decomposition(s), {total_cache_size / 1024 / 1024:.1f}MB total")

    print("\n" + "=" * 80)
    print(f"📊 Test complete! Outputs saved to: {output_dir}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
