import os
import asyncio
from pathlib import Path
from datetime import datetime
import logging

# Set up logging for the wrapper
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s — %(message)s")
logger = logging.getLogger("visual_engine_wrapper")

# Import the core pipeline components
from pipeline import decompose_image
from banner_recomposer import recompose_with_gemini_vision

async def process_ad_to_banner(
    image_source: str | Path | bytes, 
    output_base_dir: str | Path = None, 
    target_width: int = 2070, 
    target_height: int = 253, 
    temperature: float = 0.05,
    generate_banner: bool = True
) -> dict:
    """
    All-in-one wrapper function to integrate the Visual Engine into an external codebase (like FastAPI).
    
    Args:
        image_source: Absolute/relative path to the image, or raw image bytes.
        output_base_dir: Directory where the output folder should be created. Defaults to './output'.
        target_width: The pixel width of the generated panoramic banner.
        target_height: The pixel height of the generated panoramic banner.
        temperature: Creativity level of the AI (keep low, 0.05 - 0.1, to prevent duplication).
        generate_banner: If True, generates the 8:1 banner. If False, just decomposes to JSON.
        
    Returns:
        dict: Paths to the generated assets (banner image, template JSON, and the output folder).
    """
    # 1. Setup Output Directory
    if output_base_dir is None:
        output_base_dir = Path(__file__).parent / "output"
    else:
        output_base_dir = Path(output_base_dir)
        
    output_base_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = output_base_dir / f"pipeline_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 2. Handle Image Source (Bytes or Path)
    if isinstance(image_source, bytes):
        image_path = output_dir / "00_original.png"
        image_path.write_bytes(image_source)
    else:
        image_path = Path(image_source)
        if not image_path.exists():
            raise FileNotFoundError(f"Input image not found: {image_path}")
    
    try:
        # 3. Run the Decomposition Pipeline (Stages 1-3)
        logger.info("Executing Stage 1: AI Decomposition & PNG Isolation...")
        await decompose_image(str(image_path), output_dir=str(output_dir))
        
        # 4. Run Generative Banner Recomposition (Stage 4)
        logger.info("Executing Stage 2: Generative Banner Recomposition...")
        banner_output_path = output_dir / f"banner_{target_width}x{target_height}.png"
        
        await recompose_with_gemini_vision(
            output_dir=str(output_dir),
            target_w=target_width,
            target_h=target_height,
            save_path=str(banner_output_path),
            original_image_path=str(image_path),
            temperature=temperature
        )

        logger.info("✅ Visual Engine Pipeline completed successfully!")

        # 5. Return results for the external codebase to use
        return {
            "status": "success",
            "output_directory": str(output_dir),
            "banner_image_path": str(banner_output_path)
        }

    except Exception as e:
        logger.error(f"❌ Pipeline failed: {str(e)}")
        return {
            "status": "error",
            "error_message": str(e)
        }

# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Run the Visual Engine wrapper directly")
    parser.add_argument("--image", type=str, required=True, help="Path to the input advertisement image")
    parser.add_argument("--temperature", type=float, default=0.05, help="Creativity level of the AI (default: 0.05)")
    args = parser.parse_args()
    
    async def run_test():
        result = await process_ad_to_banner(
            image_source=args.image, 
            temperature=args.temperature
        )
        print("\n--- Final Output ---")
        print(json.dumps(result, indent=2))

    asyncio.run(run_test())
