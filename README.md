# ocr-service

## Prerequisites

-   Python 3.8+
-   Google Gemini API Key
-   (Optional) Docker

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
    -   Get your API Key from the [Google AI Studio](https://aistudio.google.com/app/apikey).
    -   Create or open the `.env` file in the project root.
    -   Add your API key:
        ```dotenv
        GOOGLE_API_KEY=YOUR_GEMINI_API_KEY_HERE
        ```
        _Replace `YOUR_GEMINI_API_KEY_HERE` with your actual key._

## Running the Application

### Locally

1.  **Start the FastAPI server:**

    ```bash
    uvicorn main:app --reload
    ```

    The `--reload` flag is useful for development as it restarts the server on code changes.

2.  **Access the API:**
    -   The API will be running at `http://127.0.0.1:8000`.
    -   Access the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.
    -   Access the alternative documentation (ReDoc) at `http://127.0.0.1:8000/redoc`.

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
    -   The API will be running at `http://127.0.0.1:8000`.
    -   Access the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

## API Endpoint

**POST `/process_document/`**

Processes an uploaded image file to extract and structure data.

-   **Request Body:** `file` (form-data), type `binary` (upload file).
-   **Response:** `application/json` structured according to the `Data` Pydantic model on success (HTTP 200).
-   **Error Responses:**
    -   `415 Unsupported Media Type`: If the uploaded file is not an image.
    -   `422 Unprocessable Entity`: If the processing fails specifically during data structuring.
    -   `500 Internal Server Error`: For other server-side errors during processing or file handling.

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

## CI/CD Deployment

This project includes automated CI/CD pipelines using GitHub Actions for seamless deployment to VM instances.

### Available Workflows

**Single Streamlined Pipeline** (`.github/workflows/deploy.yml`):
- 🧪 **Testing**: Validates dependencies and basic health
- 🐳 **Building**: Creates and pushes Docker images
- 🚀 **Deployment**: Smart deployment with environment detection
- ✅ **Verification**: Health checks and automatic rollback

### Quick Setup

1. **Set up GitHub Secrets** (Repository → Settings → Secrets and variables → Actions):
```

# Docker Hub

DOCKER_USERNAME=your-dockerhub-username
DOCKER_PASSWORD=your-dockerhub-password-or-token

# Production VM

PRODUCTION_VM_HOST=your-vm-ip
PRODUCTION_VM_USERNAME=ubuntu
PRODUCTION_VM_SSH_KEY=your-private-ssh-key
PRODUCTION_ENV_FILE_PATH=/home/ubuntu/ocr-service/.env

# Staging VM (for advanced workflow)

STAGING_VM_HOST=your-staging-vm-ip
STAGING_VM_USERNAME=ubuntu
STAGING_VM_SSH_KEY=your-staging-ssh-key
STAGING_ENV_FILE_PATH=/home/ubuntu/ocr-service-staging/.env

````

2. **Prepare your VM**:
```bash
# Install Docker
sudo apt update && sudo apt install -y docker.io
sudo usermod -aG docker $USER

# Create environment file
mkdir -p ~/ocr-service
echo "GOOGLE_API_KEY=your_api_key" > ~/ocr-service/.env
chmod 600 ~/ocr-service/.env
````

3. **Deploy**: Push to `main` branch or manually trigger the workflow

### Deployment Features

-   ✅ **Automatic Docker builds** with multi-architecture support
-   ✅ **Blue-green deployments** for zero-downtime updates
-   ✅ **Health checks** before switching traffic
-   ✅ **Automatic rollback** on deployment failures
-   ✅ **Image cleanup** to save disk space
-   ✅ **Backup creation** before production deployments

### Local Development with Docker

```bash
# Copy environment template
cp .env.example .env
# Edit .env with your values

# Run with Docker Compose
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

### Manual Deployment

If you need to deploy manually:

```bash
# Build and push
docker build -t your-username/ocr-service:latest .
docker push your-username/ocr-service:latest

# Deploy to VM
ssh your-vm
docker pull your-username/ocr-service:latest
docker stop ocr-service-container || true
docker rm ocr-service-container || true
docker run -d \
  --name ocr-service-container \
  --env-file /path/to/.env \
  -p 80:80 \
  --restart unless-stopped \
  your-username/ocr-service:latest
```

For detailed setup instructions, see [CICD_SETUP.md](CICD_SETUP.md).

## Health Check

The service includes a health check endpoint:

-   **GET `/health`**: Returns service status and configuration information
-   **GET `/`**: Simple status message

Use these endpoints for monitoring and load balancer health checks.
