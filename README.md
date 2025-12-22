# Nano Banana Resizer (Gemini Powered)

This is a FastAPI application that uses Google's **Gemini 3 Pro** (specifically the `gemini-3-pro-image-preview` model) to intelligently resize images to a target aspect ratio. Unlike standard cropping, this tool uses generative AI to rearrange elements and extend backgrounds, keeping critical information intact.

## Features

- **Intelligent Resizing**: Rearranges and extends image content to fit new aspect ratios (e.g., converting a landscape photo to a portrait story) without losing key subjects.
- **Modern UI**: Dark-themed, drag-and-drop web interface for easy usage.
- **API Support**: Provides a REST API endpoint for integration.

## Prerequisites

- Python 3.9+
- A Google Cloud API Key with access to Generative AI (Gemini).

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
    - Add your Google API Key:
      ```env
      GOOGLE_API_KEY=your_actual_api_key_here
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
4.  Click **Resize Image**.
5.  Wait for the AI to process and download the result.

## Tech Stack

- **Backend**: FastAPI, Google GenAI SDK (`google-genai`)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
