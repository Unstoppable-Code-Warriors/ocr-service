# CI/CD Setup Documentation

This document explains how to set up the GitHub Actions CI/CD pipeline for the OCR Service.

## Single Streamlined Pipeline

We use **one optimized pipeline** (`.github/workflows/deploy.yml`) that handles:

-   ✅ **Testing**: Basic dependency and health checks
-   ✅ **Building**: Docker image creation and push to Docker Hub
-   ✅ **Deployment**: Smart deployment to production or staging environments
-   ✅ **Verification**: Health checks and rollback on failure

## Required GitHub Secrets

Navigate to your GitHub repository → Settings → Secrets and variables → Actions, and add the following secrets:

### Docker Hub Secrets

-   `DOCKER_USERNAME`: Your Docker Hub username
-   `DOCKER_PASSWORD`: Your Docker Hub password or access token (recommended)

### VM Connection Secrets

-   `VM_HOST`: The IP address or hostname of your VM
-   `VM_USERNAME`: SSH username for your VM (e.g., `ubuntu`, `root`)
-   `VM_SSH_KEY`: Private SSH key for accessing your VM (the entire key content)
-   `VM_PORT`: (Optional) SSH port, defaults to 22 if not specified

### Environment Configuration

-   `ENV_FILE_PATH`: Absolute path to your `.env` file on the VM (e.g., `/home/ubuntu/ocr-service/.env`)

## VM Prerequisites

### 1. Install Docker on your VM

```bash
# For Ubuntu/Debian
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (replace 'ubuntu' with your username)
sudo usermod -aG docker ubuntu
# Log out and back in for group changes to take effect
```

### 2. Set up SSH Key Authentication

```bash
# On your local machine, generate SSH key pair if you don't have one
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"

# Copy public key to your VM
ssh-copy-id username@your-vm-ip

# Test SSH connection
ssh username@your-vm-ip
```

### 3. Create Environment File on VM

Create your `.env` file on the VM with required environment variables:

```bash
# Example: /home/ubuntu/ocr-service/.env
GOOGLE_API_KEY=your_google_api_key_here
# Add other environment variables as needed
```

Make sure the path matches what you set in `ENV_FILE_PATH` secret.

## Workflow Triggers

The CI/CD pipeline triggers on:

-   **Push to `main` branch**: Builds and deploys with `latest` tag
-   **Push to `develop` branch**: Builds and deploys with branch name tag
-   **Pull requests to `main`**: Builds only (no deployment)
-   **Manual trigger**: Via GitHub Actions UI

## Deployment Process

1. **Build Phase**:

    - Checks out code
    - Sets up Docker Buildx
    - Logs into Docker Hub
    - Builds Docker image with proper tags
    - Pushes image to Docker Hub

2. **Deploy Phase** (only for main/develop branches):
    - SSH into VM
    - Logs into Docker Hub on VM
    - Pulls latest image
    - Stops existing container
    - Starts new container with environment file
    - Performs health check
    - Cleans up old Docker images

## Docker Image Tagging Strategy

-   `latest`: For main branch deployments
-   `{branch-name}`: For develop and feature branch deployments
-   `{branch-name}-{commit-sha}`: Unique identifier for each build

## Monitoring and Troubleshooting

### Check container status on VM:

```bash
docker ps -a
docker logs ocr-service-container
```

### Manual deployment commands:

```bash
# Pull latest image
docker pull yourusername/ocr-service:latest

# Run container
docker run -d \
  --name ocr-service-container \
  --env-file /path/to/.env \
  -p 80:80 \
  --restart unless-stopped \
  yourusername/ocr-service:latest
```

### Cleanup old images:

```bash
docker system prune -f
docker images ocr-service --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}" | tail -n +2 | head -n -3 | awk '{print $2}' | xargs docker rmi
```

## Security Considerations

1. **Use Docker Hub Access Tokens** instead of passwords
2. **Limit SSH key access** to specific IPs if possible
3. **Keep environment files secure** with proper file permissions:
    ```bash
    chmod 600 /path/to/.env
    ```
4. **Regularly rotate secrets** in GitHub and on the VM
5. **Use a dedicated deployment user** on the VM with minimal privileges

## Customization

You can customize the workflow by:

-   Changing port mappings in the Docker run command
-   Adding additional health checks
-   Modifying the image cleanup strategy
-   Adding staging environment deployments
-   Including database migrations or other deployment steps

## Example GitHub Secrets Configuration

```
DOCKER_USERNAME=myusername
DOCKER_PASSWORD=dckr_pat_1234567890abcdef...
VM_HOST=192.168.1.100
VM_USERNAME=ubuntu
VM_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAAB...
-----END OPENSSH PRIVATE KEY-----
VM_PORT=22
ENV_FILE_PATH=/home/ubuntu/ocr-service/.env
```
