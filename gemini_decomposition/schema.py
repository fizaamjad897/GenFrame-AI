"""
Template4 schema builders — factories that produce valid canvas editor objects.

Every function returns a dict that the canvas editor can render directly.
Fields are based on the real Template4/Template6 schema from the codebase.
"""

import uuid
import time
from typing import Optional
from urllib.parse import quote as url_encode


def _uid() -> str:
    return str(uuid.uuid4())


def _timestamp_id(prefix: str = "gen") -> str:
    return f"{prefix}-{int(time.time() * 1000)}"


# ── Animation defaults ─────────────────────────────────────────────────────

def _default_animation() -> dict:
    return {
        "speed": 50,
        "style": "",
        "startTime": 0,
        "duration": 0,
        "onEnter": False,
        "onExit": False,
        "distance": 50,
    }


# ── Effects defaults ───────────────────────────────────────────────────────

def _default_image_effects() -> dict:
    return {
        "brightness": {"value": 50},
        "contrast": {"value": 50},
        "saturation": {"value": 50},
        "hue": {"value": 50},
        "grayscale": {"value": 0},
        "blur": {"value": 0},
        "tint": {"value": 0, "color": "#000000"},
        "vignette": {"value": 0},
        "transparency": {"value": 100},
    }


def _default_shape_effects() -> dict:
    return {
        "shadow": {
            "enabled": False,
            "color": "rgba(0,0,0,0.2)",
            "offsetX": 0,
            "offsetY": 0,
            "blur": 0,
        },
        "glow": {
            "enabled": False,
            "color": "#000000",
            "size": 0,
        },
    }


def _default_text_shadow() -> dict:
    return {
        "textEffect": "none",
        "angle": 0,
        "distance": 0,
        "shadowBlur": 0,
        "shadowColor": "rgb(0,0,0)",
        "transparency": 100,
        "shadowOffsetX": 0,
        "shadowOffsetY": 0,
    }


def _default_text_outline() -> dict:
    return {
        "textEffect": "none",
        "strokeWidth": 0,
        "strokeColor": "#000000",
    }


# ── HTML encoding for text Value field ─────────────────────────────────────

def _encode_text_html(
    text: str,
    font_family: str = "Montserrat",
    font_size: int = 48,
    color: str = "#000000",
    is_bold: bool = False,
    is_italic: bool = False,
    text_align: str = "left",
    line_height: str = "1.2",
) -> str:
    """Build the URL-encoded HTML that the canvas editor expects in the Value field."""
    weight = "bold" if is_bold else "normal"
    style = "italic" if is_italic else "normal"
    html = (
        f"<div style=\"text-align: {text_align}; line-height: {line_height};\">"
        f"<span style=\"font-family: {font_family}; font-size: {font_size}px; "
        f"color: {color}; font-weight: {weight}; font-style: {style};\">"
        f"{text}</span></div>"
    )
    return url_encode(html, safe="")


# ═══════════════════════════════════════════════════════════════════════════
# Object Factories
# ═══════════════════════════════════════════════════════════════════════════

def make_shape(
    *,
    name: str = "Shape",
    x: int = 0,
    y: int = 0,
    width: int = 100,
    height: int = 100,
    fill_color: str = "#000000",
    shape_type: str = "rectangle",
    border_radius: int = 0,
    opacity: float = 100,
    sort_order: int = 1,
    stroke_width: int = 0,
    stroke_color: str = "#000000",
    gradient_stops: Optional[str] = None,
    gradient_colors: Optional[list] = None,
    gradient_angle: int = 0,
    is_gradient: bool = False,
    rotate: int = 0,
) -> dict:
    obj = {
        "type": "shape",
        "shapeType": shape_type,
        "Id": _uid(),
        "Name": name,
        "DefaultColor": fill_color,
        "fillColor": fill_color,
        "StrokeWidth": stroke_width,
        "StrokeColor": stroke_color,
        "Alpha": str(int(opacity)),
        "ColorSystem": "RGB",
        "UseRgb": True,
        "borderRadius": border_radius,
        "X": x,
        "Y": y,
        "Width": width,
        "Height": height,
        "RotateDegree": rotate,
        "RotateX": 0,
        "RotateY": 0,
        "scaleX": 1,
        "scaleY": 1,
        "IsVisible": True,
        "IsHFlipped": False,
        "IsVFlipped": False,
        "locked": False,
        "opacity": opacity,
        "PageNo": 0,
        "PdfSortOrder": sort_order,
        "SortOrder": sort_order,
        "elementIndex": sort_order - 1,
        "AllowMove": "true",
        "AllowResize": "true",
        "AllowRotate": "true",
        "isEditableForRightPanel": False,
        "isGradient": is_gradient,
        "gradient": {
            "angle": gradient_angle if is_gradient else 0,
            "colors": gradient_colors if (is_gradient and gradient_colors) else [],
        },
        "gradientStops": gradient_stops or "",
        "animation": _default_animation(),
        "effects": _default_shape_effects(),
    }
    return obj


def make_text(
    *,
    name: str = "Text",
    text: str = "",
    x: int = 0,
    y: int = 0,
    width: int = 300,
    height: int = 60,
    font_family: str = "Montserrat",
    font_size: int = 48,
    color: str = "#000000",
    is_bold: bool = False,
    is_italic: bool = False,
    is_underline: bool = False,
    text_align: str = "left",
    line_spacing: str = "1.2",
    vertical_align: str = "Middle",
    opacity: float = 100,
    sort_order: int = 2,
    rotate: int = 0,
    color_system: str = "CMYK",
    default_color: str = "cmyk(0% 0% 0% 0%)",
) -> dict:
    encoded_html = _encode_text_html(
        text, font_family, font_size, color, is_bold, is_italic, text_align, line_spacing,
    )

    is_center = text_align == "center"
    is_left = text_align == "left"
    is_right = text_align == "right"
    is_justify = text_align == "justify"

    obj = {
        "type": "text",
        "Id": _uid(),
        "Name": name,
        "ColorSystem": color_system,
        "DefaultColor": default_color,
        "Value": encoded_html,
        "modifiedHtml": encoded_html,
        "Text": text,
        "IsHtml": True,
        "fontFamily": font_family,
        "fontSize": font_size,
        "color": color,
        "isBold": is_bold,
        "isItalic": is_italic,
        "isUnderline": is_underline,
        "lineSpacing": line_spacing,
        "VerticalAlign": vertical_align,
        "isJustifyCenter": is_center,
        "isJustifyLeft": is_left,
        "isJustifyRight": is_right,
        "isJustify": is_justify,
        "isBulletList": False,
        "isNumberList": False,
        "isSubScript": False,
        "isSupperScript": False,
        "textShadow": _default_text_shadow(),
        "outLine": _default_text_outline(),
        "curvedHtml": "",
        "unCurvedHtml": "",
        "valuesForLeftPanel": {
            "fontFamily": font_family,
            "fontSize": font_size,
            "color": color,
            "isBold": is_bold,
            "isItalic": is_italic,
            "isUnderline": is_underline,
            "isJustifyCenter": is_center,
            "isJustifyLeft": is_left,
            "isJustifyRight": is_right,
            "isJustify": is_justify,
            "lineSpacing": line_spacing,
        },
        "X": x,
        "Y": y,
        "Width": width,
        "Height": height,
        "PageNo": 0,
        "PdfSortOrder": sort_order,
        "SortOrder": sort_order,
        "elementIndex": sort_order - 1,
        "RotateDegree": rotate,
        "scaleX": 1,
        "scaleY": 1,
        "IsVisible": True,
        "IsHFlipped": False,
        "IsVFlipped": False,
        "locked": False,
        "opacity": opacity,
        "AllowMove": "true",
        "AllowResize": "true",
        "AllowRotate": "true",
        "isEditableForRightPanel": True,
        "isTextAdjustmentsNeeded": True,
        "isAnimated": False,
        "animation": _default_animation(),
    }
    return obj


def make_image(
    *,
    name: str = "Image",
    image_url: str = "",
    x: int = 0,
    y: int = 0,
    width: int = 400,
    height: int = 300,
    image_type: str = "Photo",
    image_extension: str = "png",
    opacity: float = 100,
    sort_order: int = 1,
    rotate: int = 0,
    lock_aspect: bool = True,
    svg_content: Optional[str] = None,
    svg_color: Optional[str] = None,
    color_system: str = "CMYK",
    default_color: str = "cmyk(0% 0% 0% 0%)",
    stencil_position_top: Optional[int] = None,
    stencil_position_left: Optional[int] = None,
) -> dict:
    obj = {
        "type": "image",
        "Id": _uid(),
        "Name": name,
        "ColorSystem": color_system,
        "DefaultColor": default_color,
        "DefaultImageUrl": image_url,
        "ImageType": image_type,
        "ImageExtension": image_extension,
        "HighResPath": image_url,
        "AlternativeImageUrls": [],
        "AlternativeImageUrlsResVersion": [],
        "croppedSrc": "none",
        "cropScaleX": 1,
        "cropScaleY": 1,
        "cropOffsetX": 0,
        "cropOffsetY": 0,
        "isCircularCrop": 0,
        "isCropped": False,
        "HighResV2Height": 0,
        "HighResV2Width": 0,
        "stencilDefaultPositionTop": stencil_position_top,
        "stencilDefaultPositionLeft": stencil_position_left,
        "X": x,
        "Y": y,
        "Width": width,
        "Height": height,
        "PageNo": 0,
        "PdfSortOrder": sort_order,
        "SortOrder": sort_order,
        "elementIndex": sort_order - 1,
        "RotateDegree": rotate,
        "scaleX": 1,
        "scaleY": 1,
        "IsVisible": True,
        "IsHFlipped": False,
        "IsVFlipped": False,
        "locked": False,
        "opacity": opacity,
        "LockAspectRatio": "true" if lock_aspect else "false",
        "IsGrayScale": False,
        "IsGrayscale": False,
        "AllowMove": "true",
        "AllowResize": "true",
        "AllowRotate": "true",
        "isEditableForRightPanel": True,
        "isAnimated": False,
        "isSelected": False,
        "originalSrc": "",
        "layerIndex": 0,
        "isGradient": False,
        "gradient": {"angle": 0, "colors": []},
        "effects": _default_image_effects(),
        "animation": _default_animation(),
    }
    if svg_content:
        obj["ImageType"] = "SVGImage"
        # Don't set DefaultColor if SVG already has inline fills — let the SVG's original colors show
        # Only use DefaultColor if explicitly provided (for user recoloring)
        obj["SvgProperty"] = {
            "content": svg_content,
            # "DefaultColor" omitted to preserve SVG's original fill colors
        }
        if svg_color:  # Only add DefaultColor if explicitly provided
            obj["SvgProperty"]["DefaultColor"] = svg_color
    return obj


# ── Template Envelope ──────────────────────────────────────────────────────

def make_template(
    *,
    objects: list[dict],
    width: int,
    height: int,
    name: str = "AI Generated Template",
    orientation: str = "Horizontal",
    base_image: str = "",
) -> dict:
    """Wrap a list of objects into a complete Template4 JSON envelope.

    width/height are required — they must come from the original image dimensions.
    """
    return {
        "Orientation": orientation,
        "SvgShapes": "",
        "TriviaQuestions": None,
        "PageWidths": {"double": width},
        "PageHeights": {"double": height},
        "Id": _uid(),
        "BankType": "Bank",
        "Name": name,
        "CsvFilePath": None,
        "Size": f"({width}x{height})",
        "IsInch": False,
        "IsDigitalMedia": True,
        "ConvertToBlackAndWhite": False,
        "AllowFontChanging": True,
        "AllowProductRename": True,
        "AllowSizeChange": True,
        "AllowCropping": False,
        "CropOnOff": False,
        "AllowFieldResize": True,
        "AllowFieldMove": True,
        "AllowFieldRotate": True,
        "AllowAddingTextField": True,
        "AllowAddingBackgroundField": True,
        "IsRssProduct": False,
        "AllowAddingImageField": True,
        "WidthCrop": width,
        "HeightCrop": height,
        "XCrop": 0,
        "YCrop": 0,
        "BaseImage": base_image,
        "IsGrayscale": False,
        "isVideoEditor": False,
        "isVideo": False,
        "isShowCrop": False,
        "scaleX": 1,
        "scaleY": 1,
        "pdfUrl": "",
        "thumbnailURL": "",
        "pages": [
            {
                "objectList": objects,
                "width": width,
                "height": height,
                "baseImage": base_image,
                "animation": {
                    "speed": 50,
                    "style": "",
                    "startTime": 0,
                    "duration": 0,
                    "onEnter": False,
                    "onExit": False,
                    "timeLineWidth": 140,
                },
            }
        ],
        "metadata": {
            "generated_by": "Design Pipeline v3",
            "template_version": "4.0",
            "ai_optimized": True,
            "quality_validated": True,
        },
    }
