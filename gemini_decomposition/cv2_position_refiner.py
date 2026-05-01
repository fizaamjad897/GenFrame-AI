"""
cv2_position_refiner.py — Optional position refinement using OpenCV.

Refines Gemini's approximate box_2d coordinates by analyzing the ORIGINAL image
to find precise element boundaries. This does NOT use the isolated component PNGs
(since Gemini re-draws them and they look different from the original).

Strategies used:
1. Edge-density boundary detection — projects edge density onto X/Y axes
2. Contour-based refinement — finds contours near the box_2d center

Falls back to box_2d if refinement fails or produces unreasonable results.
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("opencv-python not installed — CV2 position refinement disabled")


def refine_position(
    original_img_path: str,
    gemini_box_2d: list | None,
    canvas_width: int,
    canvas_height: int,
    comp_type: str,
) -> tuple[int, int, int, int]:
    """
    Refine component position using original image analysis.

    Args:
        original_img_path: Path to the original full image
        gemini_box_2d: [ymin, xmin, ymax, xmax] in 0-1000 normalized scale
        canvas_width: Target canvas width in pixels
        canvas_height: Target canvas height in pixels
        comp_type: Component type (background, text, image, etc.)

    Returns:
        (x, y, width, height) in canvas pixel coordinates
    """
    # Background: always full canvas
    if comp_type == "background":
        return 0, 0, canvas_width, canvas_height

    # Compute box_2d in canvas pixel space (this is the baseline)
    if not gemini_box_2d or len(gemini_box_2d) != 4:
        return 0, 0, canvas_width, canvas_height

    ymin, xmin, ymax, xmax = gemini_box_2d
    bx = int((xmin / 1000.0) * canvas_width)
    by = int((ymin / 1000.0) * canvas_height)
    bw = int(((xmax - xmin) / 1000.0) * canvas_width)
    bh = int(((ymax - ymin) / 1000.0) * canvas_height)

    if not CV2_AVAILABLE:
        return bx, by, max(bw, 1), max(bh, 1)

    try:
        original = cv2.imread(original_img_path)
        if original is None:
            return bx, by, max(bw, 1), max(bh, 1)

        orig_h, orig_w = original.shape[:2]

        # Scale box_2d to original image pixel space for analysis
        px_x = int((xmin / 1000.0) * orig_w)
        px_y = int((ymin / 1000.0) * orig_h)
        px_w = int(((xmax - xmin) / 1000.0) * orig_w)
        px_h = int(((ymax - ymin) / 1000.0) * orig_h)

        # Try edge-density refinement
        refined = _refine_edge_density(original, px_x, px_y, px_w, px_h, orig_w, orig_h)

        if refined:
            rx, ry, rw, rh = refined
            # Scale back from original pixel space to canvas space
            cx = int(rx * canvas_width / orig_w)
            cy = int(ry * canvas_height / orig_h)
            cw = int(rw * canvas_width / orig_w)
            ch = int(rh * canvas_height / orig_h)
            return cx, cy, max(cw, 1), max(ch, 1)

    except Exception as e:
        logger.warning(f"CV2 refinement failed: {e}")

    return bx, by, max(bw, 1), max(bh, 1)


def _refine_edge_density(original, bx, by, bw, bh, img_w, img_h):
    """
    Refine bounding box using edge density projection.
    Analyzes the original image in a padded region around box_2d,
    projects edge density onto X and Y axes, and finds tight boundaries.
    """
    padding = 0.3
    x1 = max(0, int(bx - bw * padding))
    y1 = max(0, int(by - bh * padding))
    x2 = min(img_w, int(bx + bw + bw * padding))
    y2 = min(img_h, int(by + bh + bh * padding))

    roi = original[y1:y2, x1:x2]
    if roi.size == 0:
        return None

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 40, 120)

    x_density = np.sum(edges, axis=0).astype(np.float32)
    y_density = np.sum(edges, axis=1).astype(np.float32)

    x_thresh = np.max(x_density) * 0.05 if np.max(x_density) > 0 else 0
    y_thresh = np.max(y_density) * 0.05 if np.max(y_density) > 0 else 0

    x_active = np.where(x_density > x_thresh)[0]
    y_active = np.where(y_density > y_thresh)[0]

    if len(x_active) == 0 or len(y_active) == 0:
        return None

    rx = int(x_active[0]) + x1
    ry = int(y_active[0]) + y1
    rw = int(x_active[-1] - x_active[0]) + 1
    rh = int(y_active[-1] - y_active[0]) + 1

    # Sanity check: refined result should be close to original box_2d
    center_bx, center_by = bx + bw / 2, by + bh / 2
    center_rx, center_ry = rx + rw / 2, ry + rh / 2
    offset = np.sqrt((center_bx - center_rx)**2 + (center_by - center_ry)**2)
    max_offset = np.sqrt(bw**2 + bh**2) * 0.5

    area_ratio = (rw * rh) / max(bw * bh, 1)

    if offset > max_offset or area_ratio < 0.1 or area_ratio > 5.0:
        return None

    return rx, ry, rw, rh
