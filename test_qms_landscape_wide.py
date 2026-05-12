"""
test_qms_landscape_wide.py — Test QMS pipeline for all Landscape Wide dimensions

Landscape Wide = AR >= 2.5:1 (all ultra-wide/wide strip billboards)
Includes both Batch-1 originals and Batch-2 additions.

Usage:
    python test_qms_landscape_wide.py --image /path/to/image.png
    python test_qms_landscape_wide.py --image https://example.com/image.jpg

Optional:
    --output-dir  Custom output directory (default: qms_test_outputs/landscape_wide)
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

# ── Landscape Wide Dimensions (AR >= 2.5:1) ───────────────────────────────────
QMS_LANDSCAPE_WIDE = {
    "QMS_4530X990":  (4530,  990),   # Super wide billboard      (4.58:1)
    "QMS_1728X576":  (1728,  576),   # Wide billboard            (3.0:1)
    "QMS_1280X448":  (1280,  448),   # Wide billboard            (2.86:1)
    "QMS_1152X288":  (1152,  288),   # Wide billboard            (4.0:1)
    "QMS_816X288":   (816,   288),   # Wide strip                (2.83:1)
    "QMS_768X288":   (768,   288),   # Wide strip                (2.67:1)
    "QMS_736X256":   (736,   256),   # Wide strip                (2.875:1)
}


def load_image(source: str) -> bytes:
    """Load image bytes from a local path or URL."""
    if source.startswith("http://") or source.startswith("https://"):
        print(f"   Downloading from URL...")
        with urllib.request.urlopen(source) as resp:
            return resp.read()
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
                "status": "SUCCESS",
                "time": f"{elapsed:.2f}s",
                "size": f"{len(result) / 1024:.1f}KB",
            }
        return {
            "name": name,
            "dims": f"{width}×{height}",
            "status": "FAILED",
            "time": f"{time.time() - start:.2f}s",
            "error": "Returned None",
        }
    except Exception as e:
        return {
            "name": name,
            "dims": f"{width}×{height}",
            "status": "ERROR",
            "time": f"{time.time() - start:.2f}s",
            "error": str(e)[:120],
        }


async def main():
    parser = argparse.ArgumentParser(
        description="Test QMS pipeline — Landscape Wide dimensions"
    )
    parser.add_argument("--image", required=True, help="Local path or URL to the source image")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory (default: qms_test_outputs/landscape_wide)",
    )
    args = parser.parse_args()

    group_name = "Landscape Wide"
    total = len(QMS_LANDSCAPE_WIDE)

    print("=" * 80)
    print(f"QMS Pipeline — {group_name} Dimensions ({total} formats, AR >= 2.5:1)")
    print("=" * 80)

    output_dir = Path(args.output_dir) if args.output_dir else (
        Path(__file__).parent / "qms_test_outputs" / "landscape_wide"
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n📁 Output directory: {output_dir}")

    print(f"\n📷 Loading image: {args.image}")
    image_bytes = load_image(args.image)
    print(f"   Image size: {len(image_bytes) / 1024:.1f}KB")

    print(f"\n⏳ Testing {total} {group_name} dimensions...\n")

    results = []
    total_start = time.time()

    for idx, (name, (width, height)) in enumerate(QMS_LANDSCAPE_WIDE.items(), 1):
        ar = width / height
        print(
            f"   [{idx:02d}/{total}] {name:20s} ({width:4d}×{height:4d}, AR {ar:.1f}:1)...",
            end=" ",
            flush=True,
        )
        result = await test_single_dimension(image_bytes, name, width, height, output_dir)
        results.append(result)
        icon = "✅" if result["status"] == "SUCCESS" else "❌"
        print(f"{icon} {result['time']:>8s}", flush=True)

    total_time = time.time() - total_start

    successful = [r for r in results if r["status"] == "SUCCESS"]
    failed = [r for r in results if r["status"] != "SUCCESS"]

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\n✅ Successful: {len(successful)}/{total}")
    print(f"❌ Failed:     {len(failed)}/{total}")
    print(f"⏱️  Total time: {total_time:.2f}s")

    if failed:
        print("\n❌ Failed Dimensions:")
        for r in failed:
            print(f"   • {r['name']:20s} ({r['dims']:12s}): {r.get('error', r['status'])}")

    print("\n✅ Successful Dimensions:")
    for r in successful:
        print(f"   • {r['name']:20s} ({r['dims']:12s}): {r['time']:>8s}  {r['size']:>10s}")

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
