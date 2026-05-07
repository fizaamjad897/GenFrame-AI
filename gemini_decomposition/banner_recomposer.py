"""
banner_recomposer.py — Rearrange isolated pipeline components onto a 2070×253 banner.

Background generation uses Google AI Studio REST API directly
(GOOGLE_AI_STUDIO_KEY from .env) with gemini-2.0-flash-preview-image-generation.

Takes the output directory from pipeline.py (components.json + layer_*.png files)
and produces a flat 2070×253 PNG with all components repositioned horizontally.

Usage:
    python banner_recomposer.py --dir output/pipeline_20260317_205724
    python banner_recomposer.py --image path/to/source.png   # runs full pipeline first

Architecture:
    1. Read components.json + layer_*.png from pipeline output dir
    2. Ask Gemini to plan horizontal layout for 2070×253
    3. Generate / extend background to 2070×253
    4. Composite: paste isolated layer PNGs (get_alpha_bbox for tight crop),
       re-render text cleanly with Pillow
"""

import asyncio
import argparse
import base64
import io
import json
import logging
import os
import re
import sys
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "Visual-Engine-BE-secure"))
try:
    from ooh_dimensions import get_profile as _ooh_get_profile, OOH_PROFILES
except ImportError as e:
    print(f"Error importing ooh_dimensions: {e}", file=sys.stderr)
    sys.exit(1)

try:
    from qms_dimensions import get_profile as _qms_get_profile, QMS_PROFILES
    _QMS_AVAILABLE = True
except ImportError:
    _QMS_AVAILABLE = False
    _qms_get_profile = None
    QMS_PROFILES = {}


def get_profile(target_w: int, target_h: int):
    """Return the DimProfile for the given dimensions, checking QMS profiles first."""
    if _QMS_AVAILABLE and (target_w, target_h) in QMS_PROFILES:
        return _qms_get_profile(target_w, target_h)
    return _ooh_get_profile(target_w, target_h)

load_dotenv()
load_dotenv(Path(__file__).parent / ".env")

logger = logging.getLogger("banner_recomposer")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
    datefmt="%H:%M:%S",
)

TARGET_W = 2072
TARGET_H = 252

# ── Font management ────────────────────────────────────────────────────────────

FONTS_DIR = Path(__file__).parent / "fonts"

_GF = "https://raw.githubusercontent.com/google/fonts/main"  # shorthand

FONT_URLS = {
    # ── Sans-serif: Geometric ──────────────────────────────────────────────────
    "Montserrat-Regular":     "https://raw.githubusercontent.com/JulietaUla/Montserrat/master/fonts/ttf/Montserrat-Regular.ttf",
    "Montserrat-Bold":        "https://raw.githubusercontent.com/JulietaUla/Montserrat/master/fonts/ttf/Montserrat-Bold.ttf",
    "Poppins-Regular":        f"{_GF}/ofl/poppins/Poppins-Regular.ttf",
    "Poppins-Bold":           f"{_GF}/ofl/poppins/Poppins-Bold.ttf",
    "Nunito-Regular":         f"{_GF}/ofl/nunito/Nunito-Regular.ttf",
    "Nunito-Bold":            f"{_GF}/ofl/nunito/Nunito-Bold.ttf",
    "NunitoSans-Regular":     f"{_GF}/ofl/nunitosans/NunitoSans-Regular.ttf",
    "NunitoSans-Bold":        f"{_GF}/ofl/nunitosans/NunitoSans-Bold.ttf",
    "Jost-Regular":           f"{_GF}/ofl/jost/Jost-Regular.ttf",
    "Jost-Bold":              f"{_GF}/ofl/jost/Jost-Bold.ttf",
    "Quicksand-Regular":      f"{_GF}/ofl/quicksand/Quicksand-Regular.ttf",
    "Quicksand-Bold":         f"{_GF}/ofl/quicksand/Quicksand-Bold.ttf",
    "Outfit-Regular":         f"{_GF}/ofl/outfit/Outfit-Regular.ttf",
    "Outfit-Bold":            f"{_GF}/ofl/outfit/Outfit-Bold.ttf",
    "Raleway-Regular":        f"{_GF}/ofl/raleway/Raleway-Regular.ttf",
    "Raleway-Bold":           f"{_GF}/ofl/raleway/Raleway-Bold.ttf",
    "SpaceGrotesk-Regular":   f"{_GF}/ofl/spacegrotesk/SpaceGrotesk-Regular.ttf",
    "SpaceGrotesk-Bold":      f"{_GF}/ofl/spacegrotesk/SpaceGrotesk-Bold.ttf",
    "PlusJakartaSans-Regular": f"{_GF}/ofl/plusjakartasans/PlusJakartaSans-Regular.ttf",
    "PlusJakartaSans-Bold":    f"{_GF}/ofl/plusjakartasans/PlusJakartaSans-Bold.ttf",
    "DMMono-Regular":         f"{_GF}/ofl/dmmono/DMMono-Regular.ttf",

    # ── Sans-serif: Humanist ──────────────────────────────────────────────────
    "Roboto-Regular":         "https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Regular.ttf",
    "Roboto-Bold":            "https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Bold.ttf",
    "Inter-Regular":          "https://raw.githubusercontent.com/rsms/inter/master/docs/font-files/Inter-Regular.ttf",
    "Inter-Bold":             "https://raw.githubusercontent.com/rsms/inter/master/docs/font-files/Inter-Bold.ttf",
    "Lato-Regular":           f"{_GF}/ofl/lato/Lato-Regular.ttf",
    "Lato-Bold":              f"{_GF}/ofl/lato/Lato-Bold.ttf",
    "OpenSans-Regular":       f"{_GF}/ofl/opensans/OpenSans-Regular.ttf",
    "OpenSans-Bold":          f"{_GF}/ofl/opensans/OpenSans-Bold.ttf",
    "Mulish-Regular":         f"{_GF}/ofl/mulish/Mulish-Regular.ttf",
    "Mulish-Bold":            f"{_GF}/ofl/mulish/Mulish-Bold.ttf",
    "Cabin-Regular":          f"{_GF}/ofl/cabin/Cabin-Regular.ttf",
    "Cabin-Bold":             f"{_GF}/ofl/cabin/Cabin-Bold.ttf",
    "Ubuntu-Regular":         f"{_GF}/ufl/ubuntu/Ubuntu-Regular.ttf",
    "Ubuntu-Bold":            f"{_GF}/ufl/ubuntu/Ubuntu-Bold.ttf",
    "Rubik-Regular":          f"{_GF}/ofl/rubik/Rubik-Regular.ttf",
    "Rubik-Bold":             f"{_GF}/ofl/rubik/Rubik-Bold.ttf",
    "WorkSans-Regular":       f"{_GF}/ofl/worksans/WorkSans-Regular.ttf",
    "WorkSans-Bold":          f"{_GF}/ofl/worksans/WorkSans-Bold.ttf",
    "DMSans-Regular":         f"{_GF}/ofl/dmsans/DMSans-Regular.ttf",
    "DMSans-Bold":            f"{_GF}/ofl/dmsans/DMSans-Bold.ttf",
    "Manrope-Regular":        f"{_GF}/ofl/manrope/Manrope-Regular.ttf",
    "Manrope-Bold":           f"{_GF}/ofl/manrope/Manrope-Bold.ttf",
    "NotoSans-Regular":       f"{_GF}/ofl/notosans/NotoSans-Regular.ttf",
    "NotoSans-Bold":          f"{_GF}/ofl/notosans/NotoSans-Bold.ttf",
    "IBMPlexSans-Regular":    f"{_GF}/ofl/ibmplexsans/IBMPlexSans-Regular.ttf",
    "IBMPlexSans-Bold":       f"{_GF}/ofl/ibmplexsans/IBMPlexSans-Bold.ttf",
    "FiraSans-Regular":       f"{_GF}/ofl/firasans/FiraSans-Regular.ttf",
    "FiraSans-Bold":          f"{_GF}/ofl/firasans/FiraSans-Bold.ttf",
    "SourceSans3-Regular":    f"{_GF}/ofl/sourcesans3/SourceSans3-Regular.ttf",
    "SourceSans3-Bold":       f"{_GF}/ofl/sourcesans3/SourceSans3-Bold.ttf",
    "EncodeSans-Regular":     f"{_GF}/ofl/encodesans/EncodeSans-Regular.ttf",
    "EncodeSans-Bold":        f"{_GF}/ofl/encodesans/EncodeSans-Bold.ttf",
    "Kanit-Regular":          f"{_GF}/ofl/kanit/Kanit-Regular.ttf",
    "Kanit-Bold":             f"{_GF}/ofl/kanit/Kanit-Bold.ttf",
    "Barlow-Regular":         f"{_GF}/ofl/barlow/Barlow-Regular.ttf",
    "Barlow-Bold":            f"{_GF}/ofl/barlow/Barlow-Bold.ttf",
    "Exo2-Regular":           f"{_GF}/ofl/exo2/Exo2-Regular.ttf",
    "Exo2-Bold":              f"{_GF}/ofl/exo2/Exo2-Bold.ttf",

    # ── Sans-serif: Condensed / Display ──────────────────────────────────────
    "Oswald-Regular":         "https://raw.githubusercontent.com/googlefonts/OswaldFont/master/fonts/ttf/Oswald-Regular.ttf",
    "Oswald-Bold":            "https://raw.githubusercontent.com/googlefonts/OswaldFont/master/fonts/ttf/Oswald-Bold.ttf",
    "BebasNeue-Regular":      f"{_GF}/ofl/bebasnue/BebasNeue-Regular.ttf",
    "BebasNeue-Bold":         f"{_GF}/ofl/bebasnue/BebasNeue-Regular.ttf",  # single weight
    "Anton-Regular":          f"{_GF}/apache/anton/Anton-Regular.ttf",
    "Anton-Bold":             f"{_GF}/apache/anton/Anton-Regular.ttf",       # single weight
    "FjallaOne-Regular":      f"{_GF}/ofl/fjallaone/FjallaOne-Regular.ttf",
    "FjallaOne-Bold":         f"{_GF}/ofl/fjallaone/FjallaOne-Regular.ttf",
    "FrancoisOne-Regular":    f"{_GF}/ofl/francoisone/FrancoisOne-Regular.ttf",
    "FrancoisOne-Bold":       f"{_GF}/ofl/francoisone/FrancoisOne-Regular.ttf",
    "BarlowCondensed-Regular": f"{_GF}/ofl/barlowcondensed/BarlowCondensed-Regular.ttf",
    "BarlowCondensed-Bold":   f"{_GF}/ofl/barlowcondensed/BarlowCondensed-Bold.ttf",
    "YanoneKaffeesatz-Regular": f"{_GF}/ofl/yanonekaffeesatz/YanoneKaffeesatz-Regular.ttf",
    "YanoneKaffeesatz-Bold":  f"{_GF}/ofl/yanonekaffeesatz/YanoneKaffeesatz-Bold.ttf",
    "JosefinSans-Regular":    f"{_GF}/ofl/josefinsans/JosefinSans-Regular.ttf",
    "JosefinSans-Bold":       f"{_GF}/ofl/josefinsans/JosefinSans-Bold.ttf",
    "Archivo-Regular":        f"{_GF}/ofl/archivo/Archivo-Regular.ttf",
    "Archivo-Bold":           f"{_GF}/ofl/archivo/Archivo-Bold.ttf",
    "ArchivoBlack-Regular":   f"{_GF}/ofl/archivoblack/ArchivoBlack-Regular.ttf",
    "ArchivoBlack-Bold":      f"{_GF}/ofl/archivoblack/ArchivoBlack-Regular.ttf",
    "Signika-Regular":        f"{_GF}/ofl/signika/Signika-Regular.ttf",
    "Signika-Bold":           f"{_GF}/ofl/signika/Signika-Bold.ttf",

    # ── Serif ─────────────────────────────────────────────────────────────────
    "PlayfairDisplay-Regular": f"{_GF}/ofl/playfairdisplay/PlayfairDisplay-Regular.ttf",
    "PlayfairDisplay-Bold":    f"{_GF}/ofl/playfairdisplay/PlayfairDisplay-Bold.ttf",
    "Merriweather-Regular":   f"{_GF}/ofl/merriweather/Merriweather-Regular.ttf",
    "Merriweather-Bold":      f"{_GF}/ofl/merriweather/Merriweather-Bold.ttf",
    "LibreBaskerville-Regular": f"{_GF}/ofl/librebaskerville/LibreBaskerville-Regular.ttf",
    "LibreBaskerville-Bold":  f"{_GF}/ofl/librebaskerville/LibreBaskerville-Bold.ttf",
    "ZillaSlab-Regular":      f"{_GF}/ofl/zillaslab/ZillaSlab-Regular.ttf",
    "ZillaSlab-Bold":         f"{_GF}/ofl/zillaslab/ZillaSlab-Bold.ttf",
    "Cinzel-Regular":         f"{_GF}/ofl/cinzel/Cinzel-Regular.ttf",
    "Cinzel-Bold":            f"{_GF}/ofl/cinzel/Cinzel-Bold.ttf",
    "CormorantGaramond-Regular": f"{_GF}/ofl/cormorantgaramond/CormorantGaramond-Regular.ttf",
    "CormorantGaramond-Bold": f"{_GF}/ofl/cormorantgaramond/CormorantGaramond-Bold.ttf",
    "EBGaramond-Regular":     f"{_GF}/ofl/ebgaramond/EBGaramond-Regular.ttf",
    "EBGaramond-Bold":        f"{_GF}/ofl/ebgaramond/EBGaramond-Bold.ttf",
    "CrimsonText-Regular":    f"{_GF}/ofl/crimsontext/CrimsonText-Regular.ttf",
    "CrimsonText-Bold":       f"{_GF}/ofl/crimsontext/CrimsonText-Bold.ttf",
    "LibreSerif-Regular":     f"{_GF}/ofl/libre-baskerville/LibreBaskerville-Regular.ttf",
    "NotoSerif-Regular":      f"{_GF}/ofl/notoserif/NotoSerif-Regular.ttf",
    "NotoSerif-Bold":         f"{_GF}/ofl/notoserif/NotoSerif-Bold.ttf",
    "PTSerif-Regular":        f"{_GF}/ofl/ptserif/PTSerif-Regular.ttf",
    "PTSerif-Bold":           f"{_GF}/ofl/ptserif/PTSerif-Bold.ttf",
    "Lora-Regular":           f"{_GF}/ofl/lora/Lora-Regular.ttf",
    "Lora-Bold":              f"{_GF}/ofl/lora/Lora-Bold.ttf",

    # ── Script / Handwriting ──────────────────────────────────────────────────
    "DancingScript-Regular":  f"{_GF}/ofl/dancingscript/DancingScript-Regular.ttf",
    "DancingScript-Bold":     f"{_GF}/ofl/dancingscript/DancingScript-Bold.ttf",
    "Pacifico-Regular":       f"{_GF}/ofl/pacifico/Pacifico-Regular.ttf",
    "Pacifico-Bold":          f"{_GF}/ofl/pacifico/Pacifico-Regular.ttf",
    "Lobster-Regular":        f"{_GF}/ofl/lobster/Lobster-Regular.ttf",
    "Lobster-Bold":           f"{_GF}/ofl/lobster/Lobster-Regular.ttf",
    "GreatVibes-Regular":     f"{_GF}/ofl/greatvibes/GreatVibes-Regular.ttf",
    "GreatVibes-Bold":        f"{_GF}/ofl/greatvibes/GreatVibes-Regular.ttf",
    "Satisfy-Regular":        f"{_GF}/ofl/satisfy/Satisfy-Regular.ttf",
    "Satisfy-Bold":           f"{_GF}/ofl/satisfy/Satisfy-Regular.ttf",
    "Sacramento-Regular":     f"{_GF}/ofl/sacramento/Sacramento-Regular.ttf",
    "Sacramento-Bold":        f"{_GF}/ofl/sacramento/Sacramento-Regular.ttf",
    "Allura-Regular":         f"{_GF}/ofl/allura/Allura-Regular.ttf",
    "Allura-Bold":            f"{_GF}/ofl/allura/Allura-Regular.ttf",
    "AlexBrush-Regular":      f"{_GF}/ofl/alexbrush/AlexBrush-Regular.ttf",
    "AlexBrush-Bold":         f"{_GF}/ofl/alexbrush/AlexBrush-Regular.ttf",
    "Caveat-Regular":         f"{_GF}/ofl/caveat/Caveat-Regular.ttf",
    "Caveat-Bold":            f"{_GF}/ofl/caveat/Caveat-Bold.ttf",

    # ── Decorative / Display ──────────────────────────────────────────────────
    "AlfaSlabOne-Regular":    f"{_GF}/ofl/alfaslabone/AlfaSlabOne-Regular.ttf",
    "AlfaSlabOne-Bold":       f"{_GF}/ofl/alfaslabone/AlfaSlabOne-Regular.ttf",
    "BlackHanSans-Regular":   f"{_GF}/ofl/blackhansans/BlackHanSans-Regular.ttf",
    "BlackHanSans-Bold":      f"{_GF}/ofl/blackhansans/BlackHanSans-Regular.ttf",
    "RobotoSlab-Regular":     f"{_GF}/apache/robotoslab/RobotoSlab-Regular.ttf",
    "RobotoSlab-Bold":        f"{_GF}/apache/robotoslab/RobotoSlab-Bold.ttf",
    "RobotoCondensed-Regular": f"{_GF}/apache/robotocondensed/RobotoCondensed-Regular.ttf",
    "RobotoCondensed-Bold":   f"{_GF}/apache/robotocondensed/RobotoCondensed-Bold.ttf",
}

FAMILY_MAP = {
    # ── Geometric sans ────────────────────────────────────────────────────────
    "montserrat": "Montserrat",
    "poppins": "Poppins",
    "nunito": "Nunito",
    "nunito sans": "NunitoSans",
    "nunitosans": "NunitoSans",
    "jost": "Jost",
    "quicksand": "Quicksand",
    "outfit": "Outfit",
    "raleway": "Raleway",
    "space grotesk": "SpaceGrotesk",
    "spacegrotesk": "SpaceGrotesk",
    "plus jakarta sans": "PlusJakartaSans",
    "plusjakartasans": "PlusJakartaSans",
    "jakarta": "PlusJakartaSans",

    # ── Humanist sans ─────────────────────────────────────────────────────────
    "roboto": "Roboto",
    "inter": "Inter",
    "lato": "Lato",
    "open sans": "OpenSans",
    "opensans": "OpenSans",
    "mulish": "Mulish",
    "cabin": "Cabin",
    "ubuntu": "Ubuntu",
    "rubik": "Rubik",
    "work sans": "WorkSans",
    "worksans": "WorkSans",
    "dm sans": "DMSans",
    "dmsans": "DMSans",
    "manrope": "Manrope",
    "noto sans": "NotoSans",
    "notosans": "NotoSans",
    "ibm plex sans": "IBMPlexSans",
    "ibmplexsans": "IBMPlexSans",
    "ibm plex": "IBMPlexSans",
    "fira sans": "FiraSans",
    "firasans": "FiraSans",
    "source sans": "SourceSans3",
    "source sans 3": "SourceSans3",
    "encode sans": "EncodeSans",
    "kanit": "Kanit",
    "barlow": "Barlow",
    "exo": "Exo2",
    "exo 2": "Exo2",
    "exo2": "Exo2",

    # ── Condensed / Display sans ──────────────────────────────────────────────
    "oswald": "Oswald",
    "bebas neue": "BebasNeue",
    "bebas": "BebasNeue",
    "anton": "Anton",
    "fjalla one": "FjallaOne",
    "fjallaone": "FjallaOne",
    "fjalla": "FjallaOne",
    "francois one": "FrancoisOne",
    "francoisone": "FrancoisOne",
    "barlow condensed": "BarlowCondensed",
    "barlowcondensed": "BarlowCondensed",
    "yanone kaffeesatz": "YanoneKaffeesatz",
    "yanonekaffeesatz": "YanoneKaffeesatz",
    "yanone": "YanoneKaffeesatz",
    "josefin sans": "JosefinSans",
    "josefinsans": "JosefinSans",
    "josefin": "JosefinSans",
    "archivo": "Archivo",
    "archivo black": "ArchivoBlack",
    "archivoblack": "ArchivoBlack",
    "signika": "Signika",
    "roboto condensed": "RobotoCondensed",
    "robotocondensed": "RobotoCondensed",

    # ── Serif ─────────────────────────────────────────────────────────────────
    "playfair display": "PlayfairDisplay",
    "playfair": "PlayfairDisplay",
    "merriweather": "Merriweather",
    "libre baskerville": "LibreBaskerville",
    "librebaskerville": "LibreBaskerville",
    "baskerville": "LibreBaskerville",
    "zilla slab": "ZillaSlab",
    "zillaslab": "ZillaSlab",
    "cinzel": "Cinzel",
    "cormorant garamond": "CormorantGaramond",
    "cormorantgaramond": "CormorantGaramond",
    "cormorant": "CormorantGaramond",
    "eb garamond": "EBGaramond",
    "ebgaramond": "EBGaramond",
    "crimson text": "CrimsonText",
    "crimsontext": "CrimsonText",
    "crimson": "CrimsonText",
    "noto serif": "NotoSerif",
    "notoserif": "NotoSerif",
    "pt serif": "PTSerif",
    "ptserif": "PTSerif",
    "lora": "Lora",
    "roboto slab": "RobotoSlab",
    "robotoslab": "RobotoSlab",

    # ── Script / Handwriting ──────────────────────────────────────────────────
    "dancing script": "DancingScript",
    "dancingscript": "DancingScript",
    "pacifico": "Pacifico",
    "lobster": "Lobster",
    "great vibes": "GreatVibes",
    "greatvibes": "GreatVibes",
    "satisfy": "Satisfy",
    "sacramento": "Sacramento",
    "allura": "Allura",
    "alex brush": "AlexBrush",
    "alexbrush": "AlexBrush",
    "caveat": "Caveat",
    "brush script": "DancingScript",
    "script": "DancingScript",
    "handwriting": "Caveat",

    # ── Decorative ────────────────────────────────────────────────────────────
    "alfa slab one": "AlfaSlabOne",
    "alfaslabone": "AlfaSlabOne",

    # ── Commercial → free substitutes ─────────────────────────────────────────
    "arial": "Roboto",
    "helvetica": "Roboto",
    "helvetica neue": "Roboto",
    "helveticaneue": "Roboto",
    "gotham": "Nunito",            # Nunito mirrors Gotham's rounded geometry
    "gotham rounded": "Nunito",
    "futura": "Jost",              # Jost is the closest open-source Futura clone
    "futura pt": "Jost",
    "gill sans": "Lato",
    "gillsans": "Lato",
    "proxima nova": "Montserrat",
    "proximanova": "Montserrat",
    "brandon grotesque": "Raleway",
    "brandon": "Raleway",
    "trade gothic": "Oswald",
    "tradegothic": "Oswald",
    "din": "BarlowCondensed",
    "din condensed": "BarlowCondensed",
    "akzidenz grotesk": "Roboto",
    "univers": "Roboto",
    "century gothic": "Jost",
    "trebuchet": "Cabin",
    "trebuchet ms": "Cabin",
    "verdana": "Inter",
    "tahoma": "Inter",
    "calibri": "Lato",
    "impact": "BebasNeue",
    "impact condensed": "BebasNeue",
    "rockwell": "ZillaSlab",
    "clarendon": "ZillaSlab",
    "bodoni": "PlayfairDisplay",
    "bodoni mt": "PlayfairDisplay",
    "caslon": "EBGaramond",
    "garamond": "EBGaramond",
    "adobe garamond": "EBGaramond",
    "palatino": "Lora",
    "book antiqua": "Lora",
    "minion": "Merriweather",
    "century": "LibreBaskerville",

    # ── Generic CSS families ──────────────────────────────────────────────────
    "sans-serif": "Roboto",
    "sans serif": "Roboto",
    "serif": "PlayfairDisplay",
    "monospace": "IBMPlexSans",
    "cursive": "DancingScript",
    "fantasy": "Cinzel",
    "georgia": "PlayfairDisplay",
    "times": "PlayfairDisplay",
    "times new roman": "PlayfairDisplay",
}


def _ensure_fonts():
    FONTS_DIR.mkdir(exist_ok=True)
    for name, url in FONT_URLS.items():
        dest = FONTS_DIR / f"{name}.ttf"
        if not dest.exists():
            logger.info(f"Downloading font: {name}")
            urllib.request.urlretrieve(url, dest)


def _get_font_path(family: str, bold: bool) -> Path:
    _ensure_fonts()
    base = FAMILY_MAP.get(family.strip().lower(), "Roboto")
    weight = "Bold" if bold else "Regular"
    path = FONTS_DIR / f"{base}-{weight}.ttf"
    return path if path.exists() else FONTS_DIR / "Roboto-Regular.ttf"


def _load_pil_font(family: str, bold: bool, height_px: int) -> ImageFont.FreeTypeFont:
    size = max(8, int(height_px * 0.72))
    try:
        return ImageFont.truetype(str(_get_font_path(family, bold)), size=size)
    except Exception:
        try:
            return ImageFont.load_default(size=size)
        except TypeError:
            return ImageFont.load_default()


# ── Alpha bbox (from gemini_assembler.py) ─────────────────────────────────────

def get_alpha_bbox(img: Image.Image):
    """
    Find tight bounding box of actual content within a full-canvas isolated layer PNG.
    Returns (x, y, w, h) in pixels, and the cropped RGBA image.
    Gemini outputs same-size-as-original canvases; content sits at its original position.
    """
    img_rgb = img.convert("RGB")
    data = np.array(img_rgb)
    bg_r, bg_g, bg_b = data[0, 0]

    if bg_r < 200 or bg_g < 200 or bg_b < 200:
        # Dark background — can't auto-detect edges; return full canvas
        return 0, 0, img.width, img.height, img.convert("RGBA")

    r, g, b = data[..., 0], data[..., 1], data[..., 2]
    dist = np.sqrt((r.astype(np.float32) - bg_r)**2 +
                   (g.astype(np.float32) - bg_g)**2 +
                   (b.astype(np.float32) - bg_b)**2)
    is_content = dist > 15

    h_px, w_px = is_content.shape
    rgba = np.zeros((h_px, w_px, 4), dtype=np.uint8)
    rgba[..., :3] = data
    rgba[..., 3] = 255
    rgba[..., 3][~is_content] = 0

    non_transparent = np.where(rgba[..., 3] > 0)
    if len(non_transparent[0]) == 0:
        return 0, 0, img.width, img.height, img.convert("RGBA")

    y_min, y_max = int(np.min(non_transparent[0])), int(np.max(non_transparent[0]))
    x_min, x_max = int(np.min(non_transparent[1])), int(np.max(non_transparent[1]))
    cw, ch = x_max - x_min + 1, y_max - y_min + 1

    # If content fills almost the whole canvas, just return full image
    if cw >= img.width - 20 and ch >= img.height - 20:
        return 0, 0, img.width, img.height, Image.fromarray(rgba)

    cropped = Image.fromarray(rgba).crop((x_min, y_min, x_max + 1, y_max + 1))
    return x_min, y_min, cw, ch, cropped


# ── Layout planner ─────────────────────────────────────────────────────────────

def _build_layout_prompt(components: list[dict], target_w: int, target_h: int) -> str:
    lines = []
    for i, c in enumerate(components):
        ctype = c.get("type", "?")
        desc = c.get("description", "")[:70]
        text = f' text="{c["text_content"]}"' if c.get("text_content") else ""
        weight = f' weight={c.get("font_weight","normal")}' if ctype == "text" else ""
        lines.append(f'  id={i} type={ctype}{text}{weight} desc="{desc}"')

    profile = get_profile(target_w, target_h)
    
    rules_text = chr(10).join(f"{i+1}. {rule}" for i, rule in enumerate(profile["layout_rules"]))
    warnings_text = chr(10).join(f"- {w}" for w in profile["dimension_warnings"])

    return f"""You are a professional ad designer. Arrange these ad components on {profile['canvas_description']}.

TARGET CANVAS: {target_w} × {target_h} pixels ({profile['ratio_str']} ratio)

COMPONENTS:
{chr(10).join(lines)}

LAYOUT GUIDANCE:
{profile['element_guidance']}

LAYOUT RULES:
{rules_text}
- MAINTAIN IMAGE FLOW: Do not break the image or fragment components.
- NO DUPLICATION: Do not duplicate any component. Place each element exactly once.

WARNING:
{warnings_text}

Return ONLY compact JSON on a single line (no markdown, no explanation, no whitespace):
{{"layout":[{{"id":0,"x":0,"y":0,"width":{target_w},"height":{target_h}}},{{"id":1,"x":20,"y":0,"width":300,"height":100}},...]}}"""


def _clamp_layout(layout: list[dict], tw: int, th: int) -> list[dict]:
    out = []
    for item in layout:
        x = max(0, int(item.get("x", 0)))
        y = max(0, int(item.get("y", 0)))
        w = max(1, int(item.get("width", 50)))
        h = max(1, int(item.get("height", 20)))
        if x + w > tw: w = tw - x
        if y + h > th: h = th - y
        out.append({"id": item["id"], "x": x, "y": y, "width": w, "height": h})
    return out


def _inject_missing(layout: list[dict], n: int, tw: int, th: int) -> list[dict]:
    present = {item["id"] for item in layout}
    x_cur = max((i["x"] + i["width"]) for i in layout) + 20 if layout else 0
    for mid in range(n):
        if mid not in present:
            logger.warning(f"Layout missing id={mid} — injecting at x={x_cur}")
            layout.append({"id": mid, "x": min(x_cur, tw - 60), "y": 0, "width": 60, "height": th})
            x_cur += 80
    return layout


async def _ai_studio_text(prompt: str, timeout: int = 60) -> str:
    """Call Google AI Studio text model directly using GOOGLE_AI_STUDIO_KEY."""
    import httpx
    key = os.environ.get("GOOGLE_AI_STUDIO_KEY", "")
    if not key:
        raise RuntimeError("GOOGLE_AI_STUDIO_KEY not set")
    model = os.environ.get("AI_STUDIO_TEXT_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 16384, "thinkingConfig": {"thinkingBudget": 0}},
    }
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                r = await client.post(url, json=payload)
                if r.status_code == 429:
                    await asyncio.sleep(10 * (attempt + 1)); continue
                if not r.is_success:
                    logger.error(f"AI Studio text error {r.status_code}: {r.text[:200]}")
                    raise RuntimeError(f"AI Studio text error {r.status_code}")
                data = r.json()
                parts = data["candidates"][0]["content"]["parts"]
                return "".join(p.get("text", "") for p in parts)
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"AI Studio text bad response: {e}")
        except RuntimeError:
            raise
        except Exception as e:
            logger.warning(f"AI Studio text attempt {attempt+1} failed: {e}")
            if attempt < 2: await asyncio.sleep(5 * (attempt + 1))
    raise RuntimeError("AI Studio text: all attempts failed")


async def _plan_layout(components: list[dict], target_w: int, target_h: int) -> list[dict]:
    prompt = _build_layout_prompt(components, target_w, target_h)
    logger.info("Calling Google AI Studio for layout planning...")
    try:
        raw = await _ai_studio_text(prompt)
    except Exception as e:
        logger.warning(f"AI Studio layout planning failed: {e} — using fallback")
        return _fallback_layout(components, target_w, target_h)

    # Strip markdown code fences only if present
    clean = raw.strip()
    if clean.startswith("```"):
        clean = re.sub(r"^```[a-z]*\n?", "", clean)
        clean = re.sub(r"\n?```\s*$", "", clean).strip()

    # Find the JSON object in the response
    try:
        # Try direct parse first
        data = json.loads(clean)
    except json.JSONDecodeError:
        # Try to extract the JSON object using braces matching
        start = clean.find("{")
        end = clean.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                data = json.loads(clean[start:end])
            except json.JSONDecodeError:
                logger.error(f"Layout JSON parse failed: {clean[:300]}")
                return _fallback_layout(components, target_w, target_h)
        else:
            logger.error(f"Layout JSON parse failed: {clean[:300]}")
            return _fallback_layout(components, target_w, target_h)

    layout = data.get("layout", data) if isinstance(data, dict) else data
    layout = _clamp_layout(layout, target_w, target_h)
    layout = _inject_missing(layout, len(components), target_w, target_h)
    logger.info(f"Layout planned: {len(layout)} elements")
    return layout


def _fallback_layout(components: list[dict], tw: int, th: int) -> list[dict]:
    n = max(1, len(components))
    slot_w = tw // n
    return [{"id": i, "x": i * slot_w, "y": 0, "width": slot_w, "height": th} for i in range(n)]


# ── Background ─────────────────────────────────────────────────────────────────

def _hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    if len(h) == 3: h = h[0]*2 + h[1]*2 + h[2]*2
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


async def _make_background(bg_component: dict, bg_layer_png: Path | None,
                            tw: int, th: int) -> Image.Image:
    """
    Generate tw×th background canvas. Priority order:
      1. solid_color → instant Pillow fill (no API)
      2. Existing layer PNG → stretch to target size (best quality, free)
      3. api_client.ai_studio_generate_image (gemini-3-pro-image-preview)
      4. Dark fill fallback
    """
    # 1. Solid colour — no API needed
    solid = bg_component.get("solid_color", "").strip()
    if solid and solid.startswith("#"):
        logger.info(f"Background: solid color {solid}")
        return Image.new("RGBA", (tw, th), (*_hex_to_rgb(solid), 255))

    # 2. Stretch the already-isolated background layer PNG (most common path)
    if bg_layer_png and bg_layer_png.exists():
        logger.info(f"Background: stretching existing layer PNG → {tw}×{th}")
        img = Image.open(bg_layer_png).convert("RGBA")
        return img.resize((tw, th), Image.LANCZOS)

    # 3. Google AI Studio — gemini-3-pro-image-preview
    desc = bg_component.get("description", "advertising background")
    prompt = (
        f"Generate a seamless {tw}×{th} pixel ultra-wide horizontal banner background. "
        f"Visual style: {desc}. "
        f"Rules: NO text, NO logos, NO people, NO objects, NO UI elements. "
        f"Only abstract colors, gradients, or textures. "
        f"The image must fill the full {tw}×{th} frame edge-to-edge."
    )
    logger.info("Background: calling ai_studio_generate_image...")
    try:
        from api_client import ai_studio_generate_image
        img_bytes = await ai_studio_generate_image(prompt)
        if img_bytes:
            img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
            if img.size != (tw, th):
                logger.info(f"Background: resizing from {img.size} → {tw}×{th}")
                img = img.resize((tw, th), Image.LANCZOS)
            return img
    except Exception as e:
        logger.warning(f"Background: AI Studio gen failed: {e}")

    # 4. Dark fill fallback
    logger.info("Background: using dark fill fallback")
    return Image.new("RGBA", (tw, th), (40, 40, 60, 255))


# ── Text rendering ─────────────────────────────────────────────────────────────

def _parse_color(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    if len(h) == 3: h = h[0]*2 + h[1]*2 + h[2]*2
    try:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)
    except ValueError:
        return (255, 255, 255, 255)


def _line_bbox(draw: ImageDraw.ImageDraw, text: str, font) -> tuple:
    bb = draw.textbbox((0, 0), text or "Ag", font=font)
    return bb[2] - bb[0], bb[3] - bb[1]


def _wrap_text(draw, text: str, font, max_w: int) -> list[str]:
    paragraphs = text.replace("\\n", "\n").split("\n")
    lines = []
    for para in paragraphs:
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = ""
        for word in words:
            test = (cur + " " + word).strip()
            w, _ = _line_bbox(draw, test, font)
            if w <= max_w:
                cur = test
            else:
                if cur: lines.append(cur)
                cur = word
        if cur: lines.append(cur)
    return lines or [text]


def _render_text_onto(canvas: Image.Image, component: dict, item: dict) -> Image.Image:
    text = component.get("text_content", "").strip()
    if not text:
        return canvas
    family = component.get("font_family", "Roboto")
    bold = component.get("font_weight", "normal").lower() in ("bold", "semibold", "extrabold")
    color = component.get("text_color", "#FFFFFF")
    align = component.get("text_align", "left")
    x, y, w, h = item["x"], item["y"], item["width"], item["height"]

    font = _load_pil_font(family, bold, h)
    draw = ImageDraw.Draw(canvas)
    rgba = _parse_color(color)
    lines = _wrap_text(draw, text, font, w)

    _, lh_raw = _line_bbox(draw, lines[0], font)
    line_h = max(1, int(lh_raw * 1.2))
    total_h = line_h * len(lines)

    # Shrink font until lines fit vertically
    attempts = 0
    while total_h > h and attempts < 10:
        new_size = max(8, font.size - 2)
        if new_size == font.size: break
        try:
            font = ImageFont.truetype(str(_get_font_path(family, bold)), size=new_size)
        except Exception:
            break
        lines = _wrap_text(draw, text, font, w)
        _, lh_raw = _line_bbox(draw, lines[0], font)
        line_h = max(1, int(lh_raw * 1.2))
        total_h = line_h * len(lines)
        attempts += 1

    start_y = y + max(0, (h - total_h) // 2)
    for i, line in enumerate(lines):
        lw, _ = _line_bbox(draw, line, font)
        if align == "center":
            lx = x + max(0, (w - lw) // 2)
        elif align == "right":
            lx = x + max(0, w - lw)
        else:
            lx = x
        draw.text((lx, start_y + i * line_h), line, font=font, fill=rgba)
    return canvas


# ── Layer PNG loader ───────────────────────────────────────────────────────────

def _load_layer_pngs(output_dir: Path, components: list[dict]) -> dict[int, Path | None]:
    """
    Map component list position → layer PNG path.
    Uses _layer_index if present (set by _merge_embedded_components) so that
    after embedded components are removed the surviving components still point
    to their correct on-disk PNG files.
    """
    mapping = {}
    for new_i, comp in enumerate(components):
        orig_i = comp.get("_layer_index", new_i)
        matches = sorted(output_dir.glob(f"layer_{orig_i:02d}_*.png"))
        mapping[new_i] = matches[0] if matches else None
    return mapping


# ── Component sheet builder ────────────────────────────────────────────────────

def _crop_by_box2d(img: Image.Image, box_2d: list, orig_w: int, orig_h: int) -> Image.Image:
    """
    Crop img to the bounding box from components.json (normalised 0-1000 coords).
    Used when get_alpha_bbox returns a full-canvas dark-background image so that
    small logos/icons are shown at real size rather than as invisible slivers.
    """
    if not box_2d or len(box_2d) < 4:
        return img
    ymin, xmin, ymax, xmax = box_2d
    x0 = max(0, int(xmin / 1000 * orig_w))
    y0 = max(0, int(ymin / 1000 * orig_h))
    x1 = min(img.width,  int(xmax / 1000 * orig_w))
    y1 = min(img.height, int(ymax / 1000 * orig_h))
    if x1 <= x0 or y1 <= y0:
        return img
    return img.crop((x0, y0, x1, y1))


def _build_component_sheet(
    components: list[dict],
    layer_paths: dict[int, Path | None],
    sheet_max_w: int = 2400,
    metadata: dict | None = None,
) -> Image.Image:
    """
    Build a labeled grid sheet of all isolated component PNGs.
    Gemini sees every element clearly labeled so it can compose intelligently.

    Uses box_2d-based tight cropping as fallback for full-canvas dark-background
    layers so logos/icons are NOT crushed to invisible slivers in the sheet.
    """
    THUMB_H = 320   # larger thumbnails = Gemini sees faces and logos clearly
    PAD = 10
    COLS = 4

    orig_w = (metadata or {}).get("original_width", 1000)
    orig_h = (metadata or {}).get("original_height", 1000)

    thumbs = []
    for i, comp in enumerate(components):
        path = layer_paths.get(i)

        if path and path.exists():
            try:
                img = Image.open(path).convert("RGBA")
                cx, cy, cw, ch, cropped = get_alpha_bbox(img)

                # get_alpha_bbox returns full canvas for dark-background layers.
                # Fall back to box_2d crop so tiny logos appear at real size.
                full_canvas = (cw >= img.width - 20 and ch >= img.height - 20)
                if full_canvas and comp.get("box_2d"):
                    cropped = _crop_by_box2d(img, comp["box_2d"], orig_w, orig_h)
                    cw, ch = cropped.width, cropped.height

                scale = THUMB_H / ch if ch > 0 else 1.0
                tw = max(20, int(cw * scale))
                thumb = cropped.resize((tw, THUMB_H), Image.LANCZOS)
            except Exception:
                thumb = Image.new("RGBA", (THUMB_H, THUMB_H), (80, 80, 80, 255))
        else:
            thumb = Image.new("RGBA", (THUMB_H, THUMB_H), (60, 60, 60, 255))

        thumbs.append(thumb)

    col_w = sheet_max_w // COLS
    rows = (len(thumbs) + COLS - 1) // COLS
    sheet_h = rows * (THUMB_H + PAD * 2) + PAD
    # Mid-grey background: both dark-on-light AND light-on-dark elements are visible
    sheet = Image.new("RGB", (sheet_max_w, sheet_h), (128, 128, 128))

    for idx, thumb in enumerate(thumbs):
        col = idx % COLS
        row = idx // COLS
        x = col * col_w + PAD
        y = row * (THUMB_H + PAD * 2) + PAD

        cell_bg = Image.new("RGB", (thumb.width, thumb.height), (100, 100, 100))
        sheet.paste(cell_bg, (x, y))
        sheet.paste(thumb, (x, y), thumb.split()[3] if thumb.mode == "RGBA" else None)

    return sheet


# ── Embedded component merging ────────────────────────────────────────────────

def _merge_embedded_components(components: list[dict]) -> list[dict]:
    """
    Detect and remove components whose bounding box is spatially contained
    within a photo/image/scene component. These are elements physically printed
    ON a product (logo on a bottle label, text on packaging, etc.) — they are
    already visible inside the parent layer PNG and must NOT be placed as
    separate independent layers by the recomposer.

    A component is considered embedded if:
      - Its type is logo, icon, text, shape, or button
      - Its box_2d falls entirely (with 10px tolerance) inside the box_2d of
        a photo, image, or scene component
    """
    CONTAINER_TYPES = {"photo", "image", "scene"}
    EMBEDDABLE_TYPES = {"logo", "icon", "text", "shape", "button"}
    CONTAINMENT_TOLERANCE = 20  # units in 0-1000 space

    # Collect bounding boxes for all container components
    containers = [
        c for c in components
        if c.get("type") in CONTAINER_TYPES and c.get("box_2d") and len(c["box_2d"]) == 4
    ]

    if not containers:
        return components

    merged_indices = set()
    for i, comp in enumerate(components):
        if comp.get("type") not in EMBEDDABLE_TYPES:
            continue
        box = comp.get("box_2d")
        if not box or len(box) != 4:
            continue
        cymin, cxmin, cymax, cxmax = box

        for parent in containers:
            pymin, pxmin, pymax, pxmax = parent["box_2d"]
            # Check if comp box is fully inside parent box (with tolerance)
            if (cxmin >= pxmin - CONTAINMENT_TOLERANCE and
                    cymin >= pymin - CONTAINMENT_TOLERANCE and
                    cxmax <= pxmax + CONTAINMENT_TOLERANCE and
                    cymax <= pymax + CONTAINMENT_TOLERANCE):
                logger.info(
                    f"[merge_embedded] Removing '{comp.get('type')}' "
                    f"'{comp.get('description', '')[:50]}' — "
                    f"spatially embedded inside '{parent.get('type')}' "
                    f"'{parent.get('description', '')[:40]}'"
                )
                merged_indices.add(i)
                break

    # Always stamp _layer_index so PNG loading uses original file indices
    # regardless of whether any merging happened.
    if not merged_indices:
        for i, c in enumerate(components):
            c["_layer_index"] = i
        return components

    filtered = []
    for i, c in enumerate(components):
        if i not in merged_indices:
            c = dict(c)          # shallow copy — don't mutate the original
            c["_layer_index"] = i  # preserve original on-disk index
            filtered.append(c)

    logger.info(
        f"[merge_embedded] Removed {len(merged_indices)} embedded component(s), "
        f"{len(filtered)} remain."
    )
    return filtered


# ── PRIMARY: Gemini-vision compositor ─────────────────────────────────────────

async def recompose_with_gemini_vision(
    output_dir: str | Path,
    target_w: int = TARGET_W,
    target_h: int = TARGET_H,
    save_path: str | Path | None = None,
    original_image_path: str | Path | None = None,
    temperature: float = 0.1,
) -> bytes:
    """
    Send all isolated component PNGs to Gemini image model and ask it to
    intelligently compose a target_w × target_h horizontal banner.

    Gemini understands visual hierarchy, proportions, and ad design natively —
    far better than a manual Pillow compositor.
    """
    from api_client import gemini_edit_image

    output_dir = Path(output_dir)
    components_file = output_dir / "components.json"
    if not components_file.exists():
        raise FileNotFoundError(f"components.json not found in {output_dir}")

    raw = json.loads(components_file.read_text())
    metadata = raw.get("metadata", {}) if isinstance(raw, dict) else {}
    components = raw["components"] if isinstance(raw, dict) else raw
    logger.info(f"Loaded {len(components)} components from {output_dir}")

    # Remove logos/text/icons that are physically embedded inside a photo/image
    # (e.g. logo on a bottle label, text on packaging) — they are already part
    # of the parent layer PNG and must not be placed as separate elements.
    components = _merge_embedded_components(components)

    layer_paths = _load_layer_pngs(output_dir, components)

    logger.info("Building component reference sheet...")
    sheet = _build_component_sheet(components, layer_paths, metadata=metadata)
    sheet_path = output_dir / "component_sheet.png"
    sheet.save(str(sheet_path))
    logger.info(f"Component sheet saved → {sheet_path}")

    # Collect full-resolution PNGs for photo/image/text components so Gemini sees
    # them at maximum quality rather than as small thumbnails in the sheet.
    # Text is included here so Gemini copies the exact font/style crop instead of
    # redrawing with a generic font — this is the primary fix for font-loss.
    HIGH_RES_TYPES = {"photo", "image", "logo", "text"}
    extra_image_parts: list[bytes] = []
    extra_image_types: list[str] = []
    for i, comp in enumerate(components):
        if comp.get("type", "") not in HIGH_RES_TYPES:
            continue
        lp = layer_paths.get(i)
        if lp and lp.exists():
            try:
                extra_image_parts.append(lp.read_bytes())
                extra_image_types.append(comp.get("type", "?"))
                logger.info(f"Added high-res reference: layer_{i:02d} ({comp.get('type')})")
            except Exception as e:
                logger.warning(f"Could not read layer {i} for extra parts: {e}")

    # Build component list for prompt
    comp_lines = []
    for i, c in enumerate(components):
        ctype = c.get("type", "?").upper()
        text = f', text="{c["text_content"]}"' if c.get("text_content") else ""
        comp_lines.append(f"  • {ctype}{text}: {c.get('description', '')[:80]}")

    original_context = ""
    if original_image_path and Path(original_image_path).exists():
        original_context = (
            "IMAGE 1 (original vertical ad): Use this ONLY to understand the overall "
            "visual style, color palette, and brand identity — do NOT copy its layout.\n"
        )

    extra_context = ""
    if extra_image_parts:
        has_text_refs = "text" in extra_image_types
        text_note = (
            " TEXT LAYERS ARE INCLUDED — do NOT redraw or retype text. "
            "Copy the text image crops pixel-for-pixel including their exact font, "
            "italic/condensed/oblique style, weight, size, and letter-spacing."
            if has_text_refs else ""
        )
        extra_context = (
            f"IMAGES 2–{1 + len(extra_image_parts)} (full-resolution component references): "
            "These are the exact pixel-accurate versions of the key visual components "
            f"(photos, images, logos, and text).{text_note} "
            "You MUST copy them with 100% fidelity — same face, same colors, same details. "
            "Do not redraw or reimagine them.\n"
        )

    profile = get_profile(target_w, target_h)
    warnings = profile.get("dimension_warnings", ["DO NOT change the aspect ratio"])
    warnings_text = (chr(10) + "   - ").join(warnings) if warnings else ""

    prompt = f"""You are a professional advertising layout artist. Your job is POSITIONING and SCALING only — not drawing.

{original_context}{extra_context}LAST IMAGE: Reference grid showing ALL isolated components from the advertisement.

COMPONENTS (use every single one):
{chr(10).join(comp_lines)}

YOUR ONLY TASK:
Arrange these EXACT components into a single {target_w}×{target_h} {profile['canvas_description']}. This is a strict LAYOUT job, NOT a drawing job.

CRITICAL DIRECTIVES — DO NOT IGNORE:

1. ABSOLUTE ZERO ALTERATION OF COMPONENTS:
   - YOU MUST NOT change, redraw, reimagine, or modify ANY component in any way, DONOT CHANGE HUMAN FACES USE THEM AS IT IS.
   - People, faces, products, logos, and UI elements MUST BE 100% pixel-perfect identical to the provided references. 
   - If you cannot blend something smoothly, leave it EXACTLY as it is in the reference.
   - Do NOT invent new clothing, new facial expressions, or new objects.
   - If an element looks cut off in the reference, place it at the edge of the canvas to hide the cut. Do NOT draw a new body or object around it.

2. STRICT ZERO DUPLICATION POLICY:
   - Every single component provided MUST appear EXACTLY ONCE.
   - NO EXCEPTIONS. Do not copy-paste the same person, product, logo, or text twice to fill empty space.
   - If you have empty space, fill it ONLY with abstract background color/gradient matching the original, NEVER by duplicating subjects.

3. DIMENSIONAL ACCURACY:
   - Output is ONE continuous image ({target_w}×{target_h}, {profile['ratio_str']} ratio).
   - Fill edge-to-edge with no borders or letterboxing.
   - {warnings_text}

4. SCALING AND POSITIONING:
   - {profile['element_guidance']}
   - NEVER stretch, squash, or distort any element.
   - { "Arrange elements " + profile['layout_direction'] + ": " + " -> ".join(profile['arrangement_order']) }

5. DO NOT DRAW LABELS OR NUMBERS:
   - Do NOT draw "id=", brackets "[]", bullets "•", or any layer names directly onto the banner. Lay out the actual visual assets, do not label them.

6. TEXT AND TYPOGRAPHY PRESERVATION — CRITICAL:
   - Text layers are provided as FULL-RESOLUTION pixel-accurate image crops in the reference images above.
   - You MUST use those exact image crops — do NOT retype, redraw, or re-render text in any way.
   - Treat every text component identically to a photo: paste the crop as-is, scale it to fit, never redesign it.
   - The original font may be italic, condensed, oblique, or have custom letter-spacing — preserve ALL of that by using the provided crop.
   - If the original text uses a condensed bold italic font (e.g. "24HR LASTING HOLD"), the output must show that exact image crop — NOT a new generic upright font.
   - NEVER substitute a different font. NEVER make text upright if the original is italic. NEVER round a condensed font.

Failure to follow these directives exactly will ruin the advertising campaign. Output ONLY the final {target_w}×{target_h} banner. Nothing else."""

    logger.info(f"Sending images to Gemini ({target_w}×{target_h} banner, "
                f"{len(extra_image_parts)} extra high-res parts)...")
    buf = io.BytesIO()
    sheet.save(buf, format="PNG")
    sheet_bytes = buf.getvalue()

    original_bytes = None
    if original_image_path and Path(original_image_path).exists():
        original_bytes = Path(original_image_path).read_bytes()
        logger.info(f"Included original reference image: {original_image_path}")

    # 2 retries (3 total attempts). _ai_studio_image_request handles only 429s
    # internally; all other failures surface as None so this loop fires cleanly.
    result_bytes = None
    for attempt in range(3):
        logger.info(f"Sending images to Gemini ({target_w}×{target_h} banner, "
                    f"{len(extra_image_parts)} extra high-res parts, "
                    f"attempt {attempt + 1}/3)...")
        result_bytes = await gemini_edit_image(
            sheet_bytes,
            prompt,
            timeout=300,
            original_image_bytes=original_bytes,
            temperature=temperature,
            extra_image_parts=extra_image_parts,
        )
        if result_bytes:
            break
        if attempt < 2:
            wait = (attempt + 1) * 10
            logger.warning(f"Gemini returned no image (attempt {attempt + 1}/3) — retrying in {wait}s…")
            await asyncio.sleep(wait)

    if not result_bytes:
        logger.warning("Gemini returned no image after 3 attempts — falling back to manual compositor")
        return await recompose_banner(output_dir, target_w, target_h, save_path)

    # Resize to exact target dimensions
    try:
        result_img = Image.open(io.BytesIO(result_bytes)).convert("RGB")
        if result_img.size != (target_w, target_h):
            logger.info(f"Resizing Gemini output {result_img.size} → {target_w}×{target_h}")
            result_img = result_img.resize((target_w, target_h), Image.LANCZOS)
        out_buf = io.BytesIO()
        result_img.save(out_buf, format="PNG")
        result_bytes = out_buf.getvalue()
    except Exception as e:
        logger.warning(f"Could not process result image: {e}")

    if save_path:
        Path(save_path).write_bytes(result_bytes)
        logger.info(f"Banner saved → {save_path}")

    logger.info(f"Done. Gemini-composed: {target_w}×{target_h}, {len(result_bytes):,} bytes")
    return result_bytes


# ── FALLBACK: Manual Pillow compositor ────────────────────────────────────────

async def recompose_banner(
    output_dir: str | Path,
    target_w: int = TARGET_W,
    target_h: int = TARGET_H,
    save_path: str | Path | None = None,
) -> bytes:
    """Fallback manual compositor using Gemini-planned layout."""
    output_dir = Path(output_dir)
    components_file = output_dir / "components.json"
    if not components_file.exists():
        raise FileNotFoundError(f"components.json not found in {output_dir}")

    raw = json.loads(components_file.read_text())
    components = raw["components"] if isinstance(raw, dict) else raw
    logger.info(f"Loaded {len(components)} components from {output_dir}")

    components = _merge_embedded_components(components)

    logger.info("Stage 1/3: Planning layout...")
    layout = await _plan_layout(components, target_w, target_h)
    layout_map = {item["id"]: item for item in layout}

    logger.info("Stage 2/3: Building background...")
    bg_comp = next((c for c in components if c.get("type") == "background"),
                   {"type": "background", "solid_color": "#000000"})
    bg_layer_idx = next((i for i, c in enumerate(components) if c.get("type") == "background"), 0)
    bg_layer_path = next(iter(sorted(output_dir.glob(f"layer_{bg_layer_idx:02d}_*.png"))), None)
    canvas = await _make_background(bg_comp, bg_layer_path, target_w, target_h)
    canvas = canvas.convert("RGBA")

    logger.info("Stage 3/3: Compositing elements...")
    layer_paths = _load_layer_pngs(output_dir, components)

    for i, comp in enumerate(components):
        ctype = comp.get("type", "")
        if ctype in ("background", "scene", "text"):
            continue
        item = layout_map.get(i)
        if not item:
            continue
        x, y, w, h = item["x"], item["y"], item["width"], item["height"]
        if w <= 0 or h <= 0:
            continue
        layer_path = layer_paths.get(i)
        if not layer_path or not layer_path.exists():
            continue
        try:
            layer_img = Image.open(layer_path).convert("RGBA")
        except Exception:
            continue
        cx, cy, cw, ch, cropped_rgba = get_alpha_bbox(layer_img)
        if cropped_rgba.size != (w, h):
            cropped_rgba = cropped_rgba.resize((w, h), Image.LANCZOS)
        canvas.paste(cropped_rgba, (x, y), cropped_rgba.split()[3])

    for i, comp in enumerate(components):
        if comp.get("type") != "text":
            continue
        item = layout_map.get(i)
        if not item:
            continue
        x, y, w, h = item["x"], item["y"], item["width"], item["height"]

        # Prefer compositing the original isolated text PNG to preserve exact
        # font, weight, italic styling, and design — PIL re-render loses all of that.
        layer_path = layer_paths.get(i)
        if layer_path and layer_path.exists():
            try:
                text_img = Image.open(layer_path).convert("RGBA")
                cx, cy, cw, ch, cropped_rgba = get_alpha_bbox(text_img)
                if w > 0 and h > 0:
                    if cropped_rgba.size != (w, h):
                        cropped_rgba = cropped_rgba.resize((w, h), Image.LANCZOS)
                    canvas.paste(cropped_rgba, (x, y), cropped_rgba.split()[3])
                continue  # Skip PIL re-render — original PNG used successfully
            except Exception as e:
                logger.warning(f"Could not composite text layer PNG {i}: {e} — falling back to PIL render")

        # Fallback: re-render text with PIL (loses original font/style if not in library)
        canvas = _render_text_onto(canvas, comp, item)

    final = canvas.convert("RGB").resize((target_w, target_h), Image.LANCZOS)
    buf = io.BytesIO()
    final.save(buf, format="PNG")
    result_bytes = buf.getvalue()

    if save_path:
        Path(save_path).write_bytes(result_bytes)
        logger.info(f"Banner saved → {save_path}")

    logger.info(f"Done. Manual compositor: {target_w}×{target_h}, {len(result_bytes):,} bytes")
    return result_bytes


# ── CLI ────────────────────────────────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(
        description="Recompose isolated ad components into a 2070×253 banner."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dir", "-d", help="Existing pipeline output directory")
    group.add_argument("--image", "-i", help="Source image — runs full isolation first")
    parser.add_argument("--original", help="Path to original image (if running with --dir) to use as layout reference")
    parser.add_argument("--output", "-o", default=None)
    parser.add_argument("--width",  type=int, default=2072)
    parser.add_argument("--height", type=int, default=252)
    parser.add_argument("--manual", action="store_true",
                        help="Use manual Pillow compositor instead of Gemini vision")
    parser.add_argument("--temperature", type=float, default=0.1,
                        help="Gemini creativity level (0.0=exact copy, 1.0=fully creative). "
                             "Default 0.1 minimises hallucination. (ignored with --manual)")
    args = parser.parse_args()

    if args.image:
        logger.info(f"Running isolation pipeline on: {args.image}")
        from pipeline import decompose_image
        src_path = Path(args.image)
        if not src_path.exists():
            print(f"ERROR: File not found: {src_path}", file=sys.stderr)
            sys.exit(1)
        from datetime import datetime
        out_base = Path(__file__).parent / "output"
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        pipeline_out = str(out_base / f"pipeline_{ts}")
        await decompose_image(str(src_path), output_dir=pipeline_out)
        output_dir = pipeline_out
    else:
        output_dir = args.dir

    output_path = args.output or str(Path(output_dir) / "banner_2070x253.png")

    if args.manual:
        await recompose_banner(output_dir=output_dir, target_w=args.width,
                               target_h=args.height, save_path=output_path)
    else:
        orig_path = args.original or args.image
        await recompose_with_gemini_vision(output_dir=output_dir, target_w=args.width,
                                           target_h=args.height, save_path=output_path,
                                           original_image_path=orig_path,
                                           temperature=args.temperature)

    print(f"\nBanner saved: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
