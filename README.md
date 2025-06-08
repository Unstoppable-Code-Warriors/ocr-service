# ocr-service


## Prerequisites

*   Python 3.8+
*   Google Gemini API Key
*   (Optional) Docker

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd ocr-service-repo
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your Gemini API Key:**
    *   Get your API Key from the [Google AI Studio](https://aistudio.google.com/app/apikey).
    *   Create or open the `.env` file in the project root.
    *   Add your API key:
        ```dotenv
        GOOGLE_API_KEY=YOUR_GEMINI_API_KEY_HERE
        ```
        *Replace `YOUR_GEMINI_API_KEY_HERE` with your actual key.*

## Running the Application

### Locally

1.  **Start the FastAPI server:**
    ```bash
    uvicorn main:app --reload
    ```
    The `--reload` flag is useful for development as it restarts the server on code changes.

2.  **Access the API:**
    *   The API will be running at `http://127.0.0.1:8000`.
    *   Access the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.
    *   Access the alternative documentation (ReDoc) at `http://127.0.0.1:8000/redoc`.

### Using Docker

1.  **Build the Docker image:**
    ```bash
    docker build -t ocr-service .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -d --name ocr-app -p 8000:80 ocr-service
    ```
    This will run the container in detached mode (`-d`), name it `ocr-app`, and map port 8000 on your host to port 80 in the container.

3.  **Access the API:**
    *   The API will be running at `http://127.0.0.1:8000`.
    *   Access the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

## API Endpoint

**POST `/process_document/`**

Processes an uploaded image file to extract and structure data.

*   **Request Body:** `file` (form-data), type `binary` (upload file).
*   **Response:** `application/json` structured according to the `Data` Pydantic model on success (HTTP 200).
*   **Error Responses:**
    *   `415 Unsupported Media Type`: If the uploaded file is not an image.
    *   `422 Unprocessable Entity`: If the processing fails specifically during data structuring.
    *   `500 Internal Server Error`: For other server-side errors during processing or file handling.

## Example Usage (using `curl`)

```bash
curl -X POST "http://127.0.0.1:8000/process_document/" \
-H "accept: application/json" \
-H "Content-Type: multipart/form-data" \
-F "image=@/path/to/your/image.jpeg" # Replace with the actual path to your image file


**How to Run:**

1.  Save the files into the structure described above.
2.  Make sure your `GOOGLE_API_KEY` is in the `.env` file.
3.  Install dependencies (`pip install -r requirements.txt`).
4.  Run locally with `uvicorn main:app --reload`.
5.  Go to `http://127.0.0.1:8000/docs` in your browser to test the `/process_document/` endpoint by uploading an image file.

This structure provides a clean separation of concerns (models, services, main app) and is a good starting point for a more complex application.