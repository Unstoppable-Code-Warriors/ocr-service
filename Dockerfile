# Use an official Python runtime as a parent image
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY pyproject.toml /app
COPY uv.lock /app
RUN uv sync --locked

# Copy the rest of the application code
COPY ./app /app


# Make port 80 available to the world outside this container
EXPOSE 80

# Run uvicorn when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]