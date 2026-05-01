import os
import json
import time
import glob
import logging
import numpy as np
from pathlib import Path
from PIL import Image
import boto3
import urllib.parse

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Local imports (standalone — no external project dependencies)
try:
    from gemini_decomposition import config
    from gemini_decomposition.schema import make_text, make_shape, make_image, make_template
except ImportError:
    # Direct run fallback (python gemini_assembler.py)
    import config
    from schema import make_text, make_shape, make_image, make_template

# Optional CV2 refinement
try:
    from gemini_decomposition.cv2_position_refiner import refine_position as cv2_refine
    CV2_REFINE_AVAILABLE = True
except ImportError:
    try:
        from cv2_position_refiner import refine_position as cv2_refine
        CV2_REFINE_AVAILABLE = True
    except ImportError:
        CV2_REFINE_AVAILABLE = False

# S3 Client singleton
_s3_client = None

def get_s3_client():
    global _s3_client
    if _s3_client is None:
        session = boto3.session.Session()
        _s3_client = session.client(
            "s3",
            region_name=config.DO_SPACES_REGION,
            endpoint_url=config.DO_SPACES_ENDPOINT,
            aws_access_key_id=config.DO_SPACES_KEY,
            aws_secret_access_key=config.DO_SPACES_SECRET,
        )
    return _s3_client

def upload_to_cdn(file_bytes: bytes, filename: str, content_type: str = "image/png") -> str:
    """Upload bytes to DigitalOcean Spaces, return CDN URL."""
    s3 = get_s3_client()
    key = f"gemini-decomposed/{int(time.time() * 1000)}/{filename}"

    s3.put_object(
        Bucket=config.DO_SPACES_BUCKET,
        Key=key,
        Body=file_bytes,
        ACL="public-read",
        ContentType=content_type,
    )

    if config.DO_SPACES_CDN:
        return f"{config.DO_SPACES_CDN}/{key}"
    endpoint_clean = config.DO_SPACES_ENDPOINT.replace("https://", "").replace("http://", "").strip()
    return f"https://{config.DO_SPACES_BUCKET}.{endpoint_clean}/{key}"


def get_alpha_bbox(img_path: str):
    """
    Finds the bounding box of the valid visual content.
    Gemini outputs isolated images on a flat background, but the color varies 
    (#F0F0F0, #E8E8E8, #FFFFFF). 
    We dynamically sample the top-left pixel and mask out anything similar.
    """
    with Image.open(img_path) as img:
        img_rgb = img.convert("RGB")
        data = np.array(img_rgb)
        
        # Sample the background color from the top-left pixel
        bg_r, bg_g, bg_b = data[0, 0]
        
        # Only proceed with auto-transparent masking if the top-left is relatively light/neutral
        # (Assuming Gemini isolating backgrounds are light grays or white)
        if bg_r < 200 or bg_g < 200 or bg_b < 200:
             # It's either a dark background or content that touches the corner. Don't crop.
             # E.g. the full gradient background component.
             img_rgba = img.convert("RGBA")
             return 0, 0, img.width, img.height
             
        r, g, b = data[..., 0], data[..., 1], data[..., 2]
        
        # Calculate Euclidean distance to the sampled background color
        dist = np.sqrt(
            (r.astype(np.float32) - bg_r)**2 + 
            (g.astype(np.float32) - bg_g)**2 + 
            (b.astype(np.float32) - bg_b)**2
        )
        
        # Identify pixels that are NOT the background (distance > 15)
        is_content = dist > 15
        
        # Now create the RGBA image
        h, w = is_content.shape
        rgba = np.zeros((h, w, 4), dtype=np.uint8)
        rgba[..., :3] = data
        rgba[..., 3] = 255 # Make fully opaque
        
        # Make the background transparent
        rgba[..., 3][~is_content] = 0
        
        # Find non-transparent pixels
        non_transparent = np.where(rgba[..., 3] > 0)
        
        if len(non_transparent[0]) == 0:
            return 0, 0, img.width, img.height
            
        y_min, y_max = np.min(non_transparent[0]), np.max(non_transparent[0])
        x_min, x_max = np.min(non_transparent[1]), np.max(non_transparent[1])
        
        width = x_max - x_min + 1
        height = y_max - y_min + 1
        
        # Don't crop if it takes up the whole canvas
        if width >= img.width - 20 and height >= img.height - 20:
             img_cropped = Image.fromarray(rgba)
             img_cropped.save(img_path, format="PNG")
             return 0, 0, img.width, img.height
             
        # Crop to the actual boundaries
        img_cropped = Image.fromarray(rgba).crop((x_min, y_min, x_max + 1, y_max + 1))
        
        # Overwrite the file with the cropped transparent version
        img_cropped.save(img_path, format="PNG")
        
        return int(x_min), int(y_min), int(width), int(height)


def extract_text_properties(description: str) -> dict:
    """
    Parse text component description to extract: text content, font, size, color, alignment.
    
    Examples:
    - "'Save Today' — large white serif headline, centered at top"
    - "small white sans-serif text"
    - "'Apply Now' — white sans-serif button label text"
    
    Returns: {
        "text": "Save Today",
        "font_family": "Georgia",
        "font_size": 48,
        "color": "#FFFFFF",
        "text_align": "center"
    }
    """
    desc_lower = description.lower()
    
    # Extract text content (in quotes or before dashes)
    text = ""
    if "'" in description:
        parts = description.split("'")
        if len(parts) >= 2:
            text = parts[1]
    elif '"' in description:
        parts = description.split('"')
        if len(parts) >= 2:
            text = parts[1]
    
    # Detect font family
    # NOTE: "sans-serif" check MUST come before "serif" — it's a substring of sans-serif
    font_family = "Montserrat"
    if "sans-serif" in desc_lower or "sans serif" in desc_lower:
        if "montserrat" in desc_lower:
            font_family = "Montserrat"
        elif "roboto" in desc_lower:
            font_family = "Roboto"
        elif "arial" in desc_lower:
            font_family = "Arial"
        else:
            font_family = "Montserrat"
    elif "serif" in desc_lower:
        if "georgia" in desc_lower or "times" in desc_lower:
            font_family = "Georgia"
        else:
            font_family = "Georgia"
    elif "gotham" in desc_lower:
        font_family = "Gotham Rounded Book"
    elif "impact" in desc_lower:
        font_family = "Impact"
    elif "bebas" in desc_lower:
        font_family = "Bebas Neue"
    
    # Detect font size
    font_size = 28
    if "large" in desc_lower or "big" in desc_lower or "heading" in desc_lower or "headline" in desc_lower:
        font_size = 48
    elif "small" in desc_lower or "tiny" in desc_lower or "caption" in desc_lower:
        font_size = 14
    elif "medium" in desc_lower:
        font_size = 28
    
    # Try to extract numeric size if present
    import re
    size_match = re.search(r'(\d+)\s*(?:px|pt|size)', desc_lower)
    if size_match:
        font_size = int(size_match.group(1))
    
    # Detect color
    color = "#000000"
    if "white" in desc_lower:
        color = "#FFFFFF"
    elif "gold" in desc_lower or "golden" in desc_lower:
        color = "#C9A94E"
    elif "green" in desc_lower:
        color = "#168854"
    elif "blue" in desc_lower:
        color = "#0066CC"
    elif "red" in desc_lower:
        color = "#FF0000"
    elif "black" in desc_lower:
        color = "#000000"
    elif "gray" in desc_lower or "grey" in desc_lower:
        color = "#808080"
    
    # Detect alignment
    text_align = "left"
    if "center" in desc_lower or "centered" in desc_lower:
        text_align = "center"
    elif "right" in desc_lower:
        text_align = "right"
    elif "justify" in desc_lower:
        text_align = "justify"
    
    # Detect bold/italic
    is_bold = "bold" in desc_lower
    is_italic = "italic" in desc_lower
    
    return {
        "text": text if text else "Text",
        "font_family": font_family,
        "font_size": font_size,
        "color": color,
        "text_align": text_align,
        "is_bold": is_bold,
        "is_italic": is_italic,
    }


def assemble_template(output_dir: str, width: int = None, height: int = None, orientation: str = "Horizontal"):
    """
    Reads the components.json and the PNG/SVG files from the output_dir,
    calculates bounding boxes, uploads assets, and generates a Template4 JSON.

    If width/height are not provided, they are auto-detected from the original
    image (00_original.png). This is critical because Gemini's box_2d coordinates
    are in a 0-1000 normalized space relative to the original image dimensions.
    Using mismatched canvas dimensions causes incorrect positioning.
    """
    output_dir = Path(output_dir)
    components_file = output_dir / "components.json"

    if not components_file.exists():
        logger.error(f"components.json not found in {output_dir}")
        return

    with open(components_file, "r") as f:
        raw_data = json.load(f)

    # components.json can be either:
    #   - New format: {"metadata": {...}, "components": [...]}
    #   - Legacy format: [...] (plain list)
    if isinstance(raw_data, dict) and "components" in raw_data:
        components = raw_data["components"]
        metadata = raw_data.get("metadata", {})
    else:
        components = raw_data
        metadata = {}

    # Resolve canvas dimensions (priority: caller args > metadata > original image)
    original_img_path = output_dir / "00_original.png"

    if width is None:
        width = metadata.get("original_width")
    if height is None:
        height = metadata.get("original_height")

    if (width is None or height is None) and original_img_path.exists():
        with Image.open(original_img_path) as orig_img:
            width = width or orig_img.width
            height = height or orig_img.height
            logger.info(f"Auto-detected canvas dimensions from original image: {width}x{height}")
    elif width and height:
        logger.info(f"Canvas dimensions: {width}x{height}")
    else:
        logger.error("Cannot determine canvas dimensions: no metadata, no original image, and no --width/--height provided.")
        return

    # Determine orientation from dimensions
    if orientation == "Horizontal" and height > width:
        orientation = "Vertical"
    elif orientation == "Vertical" and width > height:
        orientation = "Horizontal"
        
    all_template_objects = []
    
    # Sort order tracker
    sort_counter = 1
    
    # Process layers in order
    components_sorted = sorted(components, key=lambda x: int(x.get("layer_index", 99) if x.get("layer_index") is not None else 99))
    
    for i, comp in enumerate(components_sorted):
        # We try to use layer_index, but if this list came straight from Gemini without Qwen, it might not exist
        # Wait, if we sorted by it, we might lose the original index if they all returned 99.
        # But actually in gemini_isolate.py we did save them in order.
        # Actually in gemini_isolate.py we do not set layer_index in the components.json list objects!
        # So we just use `i` since gemini_isolate generates `layer_00...` sequentially.
        layer_idx = comp.get("layer_index", i)
        comp_type = comp.get("type", "image")
        desc = comp.get("description", f"Layer {layer_idx}")
        
        # Find the PNG file
        png_files = list(output_dir.glob(f"layer_{layer_idx:02d}_*.*")) # Can be .png or anything else, let's filter for .png
        png_files = [f for f in png_files if f.name.endswith('.png')]
        if not png_files:
            logger.warning(f"No PNG found for layer {layer_idx}")
            continue
            
        png_path = png_files[0]
        
        # Find the SVG file (if it exists)
        svg_files = list(output_dir.glob(f"layer_{layer_idx:02d}_*.svg"))
        svg_path = svg_files[0] if svg_files else None
        
        # 1. Get tight cropped dimensions from the isolated PNG.
        #    get_alpha_bbox returns pixel-accurate coordinates of the element
        #    within the full-canvas isolated image (e.g., 920,516 for a logo in a 1150x646 canvas).
        #    It also saves a cropped/transparent version of the PNG back to disk.
        crop_x, crop_y, crop_w, crop_h = get_alpha_bbox(png_path)

        box_2d = comp.get("box_2d")

        def _box2d_to_xywh(b2d):
            """Convert box_2d [ymin,xmin,ymax,xmax] in 0-1000 space → canvas (x,y,w,h)."""
            ymin, xmin, ymax, xmax = [max(0, min(1000, v)) for v in b2d]
            if ymin >= ymax or xmin >= xmax:
                return None
            return (
                int(xmin / 1000.0 * width),
                int(ymin / 1000.0 * height),
                max(1, int((xmax - xmin) / 1000.0 * width)),
                max(1, int((ymax - ymin) / 1000.0 * height)),
            )

        # 2. Choose position source based on component type:
        if comp_type == "text":
            # Text PNG is a direct bounding-box crop of the original; crop_x/crop_y are
            # relative to that small PNG (always 0,0), NOT the canvas. Must use box_2d.
            if box_2d and len(box_2d) == 4:
                result = _box2d_to_xywh(box_2d)
                x, y, w, h = result if result else (crop_x, crop_y, crop_w, crop_h)
            else:
                x, y, w, h = crop_x, crop_y, crop_w, crop_h
            logger.info(f"Layer {layer_idx} [text]: box_2d pos=({x},{y}) size=({w}x{h})")

        elif layer_idx == 0 or comp_type in ("background", "scene"):
            x, y, w, h = 0, 0, width, height
            logger.info(f"Layer {layer_idx} [{comp_type}]: full canvas")

        else:
            # For all other components (image, logo, icon, shape, etc.):
            # Prefer crop_x/crop_y — they are pixel-accurate positions from the actual
            # isolated PNG (Gemini outputs same-size canvas, get_alpha_bbox finds the element).
            # Fall back to box_2d only when crop detection failed (element fills canvas,
            # meaning get_alpha_bbox couldn't detect element boundaries — e.g. dark background).
            element_fills_canvas = (crop_w >= width * 0.85 and crop_h >= height * 0.85)

            if not element_fills_canvas:
                # Crop gave pixel-accurate canvas position — use it
                x, y, w, h = crop_x, crop_y, crop_w, crop_h
                logger.info(f"Layer {layer_idx} [{comp_type}]: crop pos=({x},{y}) size=({w}x{h})")
            elif box_2d and len(box_2d) == 4:
                # Detection failed; fall back to AI box_2d estimate
                result = _box2d_to_xywh(box_2d)
                x, y, w, h = result if result else (crop_x, crop_y, crop_w, crop_h)
                logger.info(f"Layer {layer_idx} [{comp_type}]: box_2d fallback pos=({x},{y}) size=({w}x{h})")
            else:
                x, y, w, h = crop_x, crop_y, crop_w, crop_h
                logger.info(f"Layer {layer_idx} [{comp_type}]: crop fallback pos=({x},{y}) size=({w}x{h})")
        
        # 3. Upload PNG
        with open(png_path, "rb") as f:
            png_bytes = f.read()
        
        logger.info(f"Uploading layer {layer_idx} to CDN...")
        cdn_url = upload_to_cdn(png_bytes, f"layer_{layer_idx:02d}.png", "image/png")
        
        # 3. Read SVG Content if available
        svg_content = ""
        if svg_path and svg_path.exists():
            with open(svg_path, "r") as f:
                svg_content = f.read()
                
            # Quick check for transparent SVG background missing
            if "fill=\"#F0F0F0\"" in svg_content or "fill=\"#f0f0f0\"" in svg_content:
                svg_content = svg_content.replace("fill=\"#F0F0F0\"", "fill=\"transparent\"")
                svg_content = svg_content.replace("fill=\"#f0f0f0\"", "fill=\"transparent\"")
                
            # Format nicely for the JSON 
            svg_content = urllib.parse.quote(svg_content)
        
        # 4. Construct JSON Object
        if comp_type == "text":
            # Start with description-parsed defaults
            text_props = extract_text_properties(comp.get("description", "Text"))

            # Override with direct AI-returned fields (more accurate than keyword parsing)
            if comp.get("text_content", "").strip():
                text_props["text"] = comp["text_content"].strip()
            if comp.get("font_family", "").strip():
                text_props["font_family"] = comp["font_family"].strip()
            if comp.get("font_weight", "").strip():
                fw = comp["font_weight"].strip().lower()
                text_props["is_bold"] = fw in ("bold", "semibold", "extrabold", "black")
            if comp.get("text_color", "").strip():
                text_props["color"] = comp["text_color"].strip()
            if comp.get("text_align", "").strip():
                text_props["text_align"] = comp["text_align"].strip()

            # Calculate font size from bounding box height (far more accurate than keywords)
            # h is the pixel height of the text box on the canvas
            if h > 0:
                line_count = max(1, text_props["text"].count("\n") + 1)
                # ~75% of box height for single-line; divide by line count for multi-line
                text_props["font_size"] = max(8, int(h * 0.75 / line_count))

            obj = make_text(
                name=f"Text: {text_props['text'][:30]}",
                text=text_props["text"],
                x=x, y=y, width=w, height=h,
                font_family=text_props["font_family"],
                font_size=text_props["font_size"],
                color=text_props["color"],
                is_bold=text_props["is_bold"],
                is_italic=text_props["is_italic"],
                text_align=text_props["text_align"],
                sort_order=sort_counter,
                color_system="RGB",
                default_color=text_props["color"],
            )
            logger.info(f"Created text object: '{text_props['text']}' font={text_props['font_family']} size={text_props['font_size']} color={text_props['color']} align={text_props['text_align']}")
        elif comp_type == "shape" or comp_type == "button":
            # If we don't have an SVG for the shape, we just upload it as an image
            if svg_content:
                obj = make_image(
                    name=desc[:30],
                    image_url=cdn_url,
                    x=x, y=y, width=w, height=h,
                    image_type="Svg",
                    sort_order=sort_counter,
                    svg_content=svg_content
                )
            else:
                obj = make_image(
                    name=desc[:30],
                    image_url=cdn_url,
                    x=x, y=y, width=w, height=h,
                    image_type="Photo",
                    sort_order=sort_counter
                )
        elif comp_type == "logo" or comp_type == "icon":
            obj = make_image(
                name=f"{comp_type}: {desc[:22]}",
                image_url=cdn_url,
                x=x, y=y, width=w, height=h,
                image_type="Svg" if svg_content else "Photo", # Svg is preferred for logos
                sort_order=sort_counter,
                svg_content=svg_content if svg_content else None
            )
        else:
            # Backgrounds, scenes, photos, illustrations
            obj = make_image(
                name=desc[:30],
                image_url=cdn_url,
                x=x, y=y, width=w, height=h,
                image_type="Photo",
                sort_order=sort_counter
            )
            
        # Lock background/scene layers to prevent accidental selection/dragging
        if layer_idx == 0 or comp_type in ("background", "scene"):
            obj["locked"] = True

        all_template_objects.append(obj)
        sort_counter += 1
        
    # Generate final template
    logger.info("Assembling final Template4...")
    template = make_template(
        objects=all_template_objects,
        width=width,
        height=height,
        name="Gemini Decomposed Design",
        orientation=orientation
    )
    
    output_path = output_dir / "final_template.json"
    with open(output_path, "w") as f:
        json.dump(template, f, indent=2)
        
    logger.info(f"Successfully generated {output_path}")
    return template


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Assemble separated components into Template JSON")
    parser.add_argument("--dir", type=str, required=True, help="Directory containing components.json and images")
    parser.add_argument("--width", type=int, default=None, help="Canvas width (auto-detected from original image if omitted)")
    parser.add_argument("--height", type=int, default=None, help="Canvas height (auto-detected from original image if omitted)")

    args = parser.parse_args()
    assemble_template(args.dir, args.width, args.height)
