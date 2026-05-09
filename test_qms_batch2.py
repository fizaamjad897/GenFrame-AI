"""
test_qms_batch2.py — Run all 16 batch-2 QMS dimensions in one go

Covers all three groups (landscape wide, landscape moderate, portrait moderate).

Usage:
    python test_qms_batch2.py --image /path/to/image.png
    python test_qms_batch2.py --image https://example.com/image.jpg

Optional:
    --output-dir  Custom output directory (default: qms_test_outputs/batch2)
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

# ── All 16 batch-2 test dimensions ────────────────────────────────────────────
QMS_BATCH2 = {
    # ── Landscape Wide (AR >= 2.5:1) ──────────────────────────────────────────
    "QMS_4530X990":  (4530,  990),   # Super wide billboard      (4.58:1)  mirrors OOH 3924×972
    "QMS_1728X576":  (1728,  576),   # Wide billboard            (3.0:1)   same ratio as 1728×432
    "QMS_1280X448":  (1280,  448),   # Wide billboard            (2.86:1)  neighbours OOH 1280×384
    "QMS_1152X288":  (1152,  288),   # Wide billboard            (4.0:1)   same ratio as QMS 1728×432
    "QMS_816X288":   (816,   288),   # Wide strip                (2.83:1)  between QMS 760×240 & 864×288
    "QMS_768X288":   (768,   288),   # Wide strip                (2.67:1)  neighbour of 816×288
    "QMS_736X256":   (736,   256),   # Wide strip                (2.875:1) direct neighbour of QMS 760×240
    # ── Landscape Moderate (AR 1.0:1 – 2.5:1) ────────────────────────────────
    "QMS_1680X810":  (1680,  810),   # Moderate landscape banner (2.07:1)  mirrors OOH 1952×896
    "QMS_864X480":   (864,   480),   # Moderate landscape banner (1.8:1)   mirrors OOH 1232×672
    "QMS_608X304":   (608,   304),   # Standard 2:1 banner       (2.0:1)   mirror of OOH 800×400
    "QMS_600X320":   (600,   320),   # Moderate banner           (1.875:1) proven 2:1 template
    "QMS_600X280":   (600,   280),   # Moderate banner           (2.14:1)  mirrors OOH 840×360
    # ── Portrait Moderate (AR 1:1.6 – 1:2.25) ────────────────────────────────
    "QMS_648X1296":  (648,  1296),   # Portrait banner  1:2      (1:2.00)  larger 1:2 template
    "QMS_480X960":   (480,   960),   # Portrait banner  1:2      (1:2.00)  direct mirror of OOH 504×1008
    "QMS_432X768":   (432,   768),   # Portrait banner  9:16     (1:1.78)  mirrors OOH 768×1152
    "QMS_360X720":   (360,   720),   # Portrait banner  1:2      (1:2.00)  compact same template as 480×960
}

GROUPS = {
    "Landscape Wide":     ["QMS_4530X990", "QMS_1728X576", "QMS_1280X448", "QMS_1152X288",
                           "QMS_816X288", "QMS_768X288", "QMS_736X256"],
    "Landscape Moderate": ["QMS_1680X810", "QMS_864X480", "QMS_608X304", "QMS_600X320", "QMS_600X280"],
    "Portrait Moderate":  ["QMS_648X1296", "QMS_480X960", "QMS_432X768", "QMS_360X720"],
}


def load_image(source: str) -> bytes:
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
            (output_dir / f"{name}_{width}x{height}.png").write_bytes(result)
            return {"name": name, "dims": f"{width}×{height}", "status": "SUCCESS",
                    "time": f"{elapsed:.2f}s", "size": f"{len(result) / 1024:.1f}KB"}
        return {"name": name, "dims": f"{width}×{height}", "status": "FAILED",
                "time": f"{time.time() - start:.2f}s", "error": "Returned None"}
    except Exception as e:
        return {"name": name, "dims": f"{width}×{height}", "status": "ERROR",
                "time": f"{time.time() - start:.2f}s", "error": str(e)[:120]}


async def main():
    parser = argparse.ArgumentParser(description="Test QMS batch-2 — all 16 dimensions")
    parser.add_argument("--image", required=True, help="Local path or URL to the source image")
    parser.add_argument("--output-dir", default=None,
                        help="Output directory (default: qms_test_outputs/batch2)")
    args = parser.parse_args()

    total = len(QMS_BATCH2)

    print("=" * 80)
    print(f"QMS Pipeline — Batch-2 All Dimensions ({total} formats)")
    print("  7 × Landscape Wide  |  5 × Landscape Moderate  |  4 × Portrait Moderate")
    print("=" * 80)

    output_dir = Path(args.output_dir) if args.output_dir else (
        Path(__file__).parent / "qms_test_outputs" / "batch2"
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n📁 Output directory: {output_dir}")

    print(f"\n📷 Loading image: {args.image}")
    image_bytes = load_image(args.image)
    print(f"   Image size: {len(image_bytes) / 1024:.1f}KB")

    print(f"\n⏳ Testing {total} dimensions...\n")

    results = {}
    total_start = time.time()
    idx = 0

    for group, keys in GROUPS.items():
        print(f"  ── {group} {'─' * (54 - len(group))}")
        for name in keys:
            idx += 1
            width, height = QMS_BATCH2[name]
            ar = width / height
            ar_str = f"{ar:.2f}:1" if width > height else f"1:{height/width:.2f}"
            print(
                f"   [{idx:02d}/{total}] {name:20s} ({width:4d}×{height:4d}, {ar_str:>8s})...",
                end=" ", flush=True,
            )
            result = await test_single_dimension(image_bytes, name, width, height, output_dir)
            results[name] = result
            icon = "✅" if result["status"] == "SUCCESS" else "❌"
            print(f"{icon} {result['time']:>8s}", flush=True)
        print()

    total_time = time.time() - total_start

    successful = [r for r in results.values() if r["status"] == "SUCCESS"]
    failed     = [r for r in results.values() if r["status"] != "SUCCESS"]

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\n✅ Successful: {len(successful)}/{total}")
    print(f"❌ Failed:     {len(failed)}/{total}")
    print(f"⏱️  Total time: {total_time:.2f}s")

    # Per-group summary
    print()
    for group, keys in GROUPS.items():
        g_ok  = sum(1 for k in keys if results[k]["status"] == "SUCCESS")
        g_tot = len(keys)
        bar   = "✅" * g_ok + "❌" * (g_tot - g_ok)
        print(f"  {group:22s}  {bar}  {g_ok}/{g_tot}")

    if failed:
        print("\n❌ Failed Dimensions:")
        for r in failed:
            print(f"   • {r['name']:20s} ({r['dims']:12s}): {r.get('error', r['status'])}")

    print("\n✅ Successful Dimensions:")
    for r in successful:
        print(f"   • {r['name']:20s} ({r['dims']:12s}): {r['time']:>8s}  {r['size']:>10s}")

    cache_root = Path(__file__).parent / "ooh_decomposition_cache"
    if cache_root.exists():
        entries = list(cache_root.glob("*"))
        size_mb = sum(f.stat().st_size for f in cache_root.glob("*/*") if f.is_file()) / 1024 / 1024
        print(f"\n💾 Cache: {len(entries)} decomposition(s), {size_mb:.1f}MB total")

    print("\n" + "=" * 80)
    print(f"📊 Test complete! Outputs saved to: {output_dir}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
