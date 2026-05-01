# Visual Engine: AI-Native Ad Decomposition Pipeline

This project is a powerful AI-driven pipeline that reverse-engineers flat, static advertisements (JPEGs/PNGs) back into editable, multi-layer design templates and automatically recomposes them into extreme 8:1 panoramic banners.

It leverages the **Google AI Studio APIs** (`gemini-2.5-pro` for vision analysis and `gemini-3-pro-image-preview` for raster isolation/generation) alongside `Pillow` and `numpy` for pixel-accurate cropping and assembly.

---

## 📂 Core Files Architecture

The backend consists of **8 critical Python files**. The pipeline flows sequentially through these scripts:

1. **`pipeline.py` (The Orchestrator)**
   - The main entry point. It manages the asynchronous execution of the 4-stage pipeline (Analysis -> Isolation -> Cropping -> Assembly).
2. **`gemini_isolate.py` (Stage 1 & 2: Analysis and Generation)**
   - Sends the raw image to Gemini to identify all visual components (text, logos, background).
   - Dynamically prompts Gemini to erase backgrounds and isolate each specific element into full-canvas PNGs.
3. **`gemini_assembler.py` (Stage 3 & 4A: Cropping and JSON Template)**
   - Uses `numpy` to convert Gemini's solid-color background masks into tight, transparent PNG crops.
   - Maps the coordinates and builds the final `final_template.json` (Template4 Format) for frontend canvas editors.
   - Uploads final transparent assets to a DigitalOcean Spaces CDN.
4. **`banner_recomposer.py` (Stage 4B: Generative Recomposition)**
   - Takes all the isolated PNGs, compiles them into a grid, and sends them to Gemini with an aggressive "Art Director" prompt to generate an ultra-wide 8:1 banner (e.g., 2070x253).
5. **`api_client.py` (Network Layer)**
   - Centralized handler for all Google AI Studio HTTP requests.
6. **`schema.py` (Data Structures)**
   - Defines the JSON output structures (`make_text`, `make_image`) used to build the Template4 format.
7. **`config.py`**
   - securely loads all environment variables.
8. **`.env`**
   - Stores your `GOOGLE_AI_STUDIO_KEY` and DigitalOcean Spaces keys.

*(Note: `server.py` is the FastAPI wrapper that exposes this pipeline to your frontend).*

---

## 🚀 How to Run the Pipeline

### 1. Prerequisite Setup
Ensure your virtual environment is active and you have installed the requirements (like `Pillow`, `numpy`, `httpx`, `boto3`). 
Ensure your `.env` file contains your `GOOGLE_AI_STUDIO_KEY`.

### 2. How to Run the Pipeline
There are two primary ways to run the decomposition and banner generation process.

**Method A: Via FastAPI (For Production / Frontend Integration)**
This is the recommended method for integrating with a frontend. Start the server and send a POST request with the image.

1. **Start the server:**
```bash
python server.py
# (Runs on port 8080 by default)
```

2. **Call the API:**
```bash
curl -X POST "http://localhost:8080/api/decompose" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "image_file=@tests/test6.png" \
  -F "temperature=0.1"
```
**Response:**
```json
{
  "banner_url": "/Users/.../pipeline_20260429_191939/banner_2070x253.png",
  "status": "success"
}
```

**Method B: The All-In-One Terminal Command (For Local Testing)**
If you just want to run the pipeline directly via the command line without the API server, use the wrapper script:

```bash
cd "/Users/abdullah/Desktop/Techinoid/Github Projects/Visual-Engine-BE/gemini_decomposition"
python wrapper.py --image "tests/test6.png" --temperature=0.1
```

**What happens under the hood?**
1. It creates a timestamped folder inside `output/`.
2. It detects and isolates layers (`layer_00_background.png`, `layer_01_logo.png`, etc.).
3. It immediately generates the final 8:1 wide output: `banner_2070x253.png`.

### 3. Run ONLY Banner Recomposition (Testing Layouts)
If you already ran the pipeline and just want to test adjusting the generative banner layout without waiting for all the layers to extract again, you can pass the existing output directory to the recomposer directly:

```bash
python banner_recomposer.py --dir "output/pipeline_20260429_143356" --original "path/to/original.jpeg" --temperature 0.05
```

**The `--temperature` Flag:**
- **What it does:** It controls the "creativity" of the Gemini image model. 
- **Why it matters:** Generative image models natively struggle with duplicating objects or hallucinating details when asked to drastically alter aspect ratios. Lowering the temperature to `0.05` or `0.1` restricts the model's creative variance, forcing it to strictly obey the prompt guardrails (e.g., "NO DUPLICATION", "STRICT ONE-INSTANCE RULE", "DO NOT REDRAW"). 
- **Usage:** If you notice the generated banner is duplicating a phone or altering a logo, run it again with `--temperature 0.05`.

---

## ⚙️ Configuration & Guardrails

### SVGs vs PNGs
By default, the pipeline **disables SVG generation** for logos and shapes to improve speed and stability. All components are extracted as high-fidelity transparent PNGs. If you need vector paths in the future, the SVG generation code exists in `gemini_isolate.py` but is commented out.

### Anti-Duplication Rules & Temperature
The prompt inside `banner_recomposer.py` contains extremely aggressive guardrails to prevent the model from stacking components vertically into a square. However, the prompt alone isn't always enough. The key to enforcing copy-paste fidelity and stopping cloning is to **combine the strict prompt with a very low temperature parameter** (passed natively to the Gemini API via `api_client.py`).
