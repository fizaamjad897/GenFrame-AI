"""
test_qms_single.py — Test QMS/OOH pipeline for a single dimension

Usage:
    python test_qms_single.py --image /path/to/image.jpg --dim QMS_1472X480
    python test_qms_single.py --image https://example.com/image.jpg --dim OOH_1344X432
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

from main import OOH_MEDIA_SITE_DIMENSIONS
from ooh_pipeline import ooh_resize


def load_image(source: str) -> bytes:
    if source.startswith("http://") or source.startswith("https://"):
        print(f"Downloading from URL...")
        with urllib.request.urlopen(source) as resp:
            return resp.read()
    return Path(source).read_bytes()


async def main():
    parser = argparse.ArgumentParser(description="Test OOH/QMS pipeline for a single dimension")
    parser.add_argument("--image", required=True, help="Local path or URL to the source image")
    parser.add_argument("--dim", required=True, help="Dimension code e.g. QMS_1472X480")
    args = parser.parse_args()

    dim_code = args.dim.upper()
    if dim_code not in OOH_MEDIA_SITE_DIMENSIONS:
        print(f"ERROR: '{dim_code}' not found in OOH_MEDIA_SITE_DIMENSIONS.")
        print(f"\nAvailable dimensions:")
        for code in sorted(OOH_MEDIA_SITE_DIMENSIONS):
            w, h = OOH_MEDIA_SITE_DIMENSIONS[code]
            print(f"  {code:20s} ({w}×{h})")
        sys.exit(1)

    width, height = OOH_MEDIA_SITE_DIMENSIONS[dim_code]

    print("=" * 60)
    print(f"Dimension : {dim_code} ({width}×{height})")
    print(f"Image     : {args.image}")
    print("=" * 60)

    image_bytes = load_image(args.image)
    print(f"Image size: {len(image_bytes) / 1024:.1f}KB\n")

    print(f"Running pipeline...", flush=True)
    start = time.time()
    result = await ooh_resize(image_bytes, width, height)
    elapsed = time.time() - start

    if result:
        output_dir = Path(__file__).parent / "qms_test_outputs"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{dim_code}_{width}x{height}.png"
        output_path.write_bytes(result)
        print(f"\n✅ SUCCESS in {elapsed:.2f}s")
        print(f"   Output : {output_path}")
        print(f"   Size   : {len(result) / 1024:.1f}KB")
    else:
        print(f"\n❌ FAILED in {elapsed:.2f}s — pipeline returned None")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
