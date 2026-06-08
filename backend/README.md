# Visual Engine Backend - Authentication & Image Processing API

This is the backend service for Visual Engine, a FastAPI-based application with JWT authentication, image processing via Google Gemini AI, and usage tracking with MongoDB.

## Features

- **User Authentication**: JWT-based auth with registration, login, and password reset
- **Image Processing**: AI-powered image resizing using Google Gemini 3 Pro
- **Usage Tracking**: Track user API hits with plan-based limits (Starter: 50 demo hits, then 1,000 monthly)
- **MongoDB Integration**: Persistent user data and usage tracking
- **CORS Support**: Built-in CORS middleware for frontend integration
- **Email Password Reset**: Automated password reset emails with secure tokens
- **Cloud Storage**: Automatically uploads processed images to Digital Ocean Spaces.

## Prerequisites

- Python 3.9+
- A Google Cloud API Key with access to Generative AI (Gemini).
- Digital Ocean Spaces account for image storage.

## Setup

1.  **Clone the repository** (if applicable) or navigate to the project folder.

2.  **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**:
    - Create a `.env` file in the root directory.
    - Add your API keys and configuration:
      ```env
      GOOGLE_API_KEY=your_actual_google_api_key_here
      ACCESS_KEY_ID=your_digital_ocean_access_key
      SECRET_KEY=your_digital_ocean_secret_key
      ENDPOINT=https://your-region.digitaloceanspaces.com
      SPACENAME=your_space_name
      ```

## Running the App

Start the server using Uvicorn:

```bash
uvicorn main:app --reload
```

The application will be available at: **http://localhost:8000**

## Usage

1.  Open the web interface in your browser.
2.  Drag and drop an image.
3.  Select a target aspect ratio (e.g., 16:9, 9:16) or enter a custom one.
4.  **Optional**: Enter a custom prompt for advanced editing (e.g., "make it black and white", "add cartoon effects").
5.  Click **Process Image**.
6.  Wait for the AI to process and download the result.

## API Documentation

### Endpoint: `POST /resize`

Processes an image using Gemini AI for resizing and/or custom editing.

#### Request Body (Form Data)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File | Yes | Image file to process (supported formats: PNG, JPG, JPEG, etc.) |
| `aspect_ratio` | String | Yes | Target aspect ratio (e.g., "16:9", "1:1", "4:3") |
| `prompt` | String | No | Custom prompt for image editing. If not provided, uses default resizing prompt |

#### Response

**Success (200):**
```json
{
  "url": "https://your-space.region.digitaloceanspaces.com/resized_images/20260101_120000_abc123.png",
  "name": "20260101_120000_abc123.png"
}
```

**Error (500):**
```json
{
  "detail": "Error message describing what went wrong"
}
```

#### Example Usage

**Using curl:**
```bash
curl -X POST "http://localhost:8000/resize" \
  -F "file=@image.jpg" \
  -F "aspect_ratio=16:9" \
  -F "prompt=make this image look like a painting"
```

**Using Python:**
```python
import requests

with open('image.jpg', 'rb') as f:
    files = {'file': f}
    data = {
        'aspect_ratio': '16:9',
        'prompt': 'add a sunset background'  # optional
    }
    response = requests.post('http://localhost:8000/resize', files=files, data=data)
    print(response.json())
```

#### Notes

- Images are automatically uploaded to Digital Ocean Spaces and publicly accessible via the returned URL
- The `prompt` field allows for flexible image editing beyond just resizing
- If no `prompt` is provided, the system uses a default prompt that focuses on intelligent resizing while preserving image content
- Processing time depends on image size and complexity (typically 10-30 seconds)

## Tech Stack

- **Backend**: FastAPI, Google GenAI SDK (`google-genai`)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Storage**: Digital Ocean Spaces (S3-compatible)
- **AI Model**: Google Gemini 3 Pro (`gemini-3-pro-image-preview`)
