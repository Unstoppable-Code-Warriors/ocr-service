from fastapi import FastAPI, HTTPException, status, Query
from models import Data
from services.ocr_service import process_image_to_structured_data
import httpx  # HTTP client
import asyncio

app = FastAPI(
    title="OCR and Data Structuring Service",
    description="API for processing document images using Gemini and structuring extracted data."
)

@app.get("/health")
async def read_root():
    return {"message": "OCR Service is running. Go to /docs for API documentation."}

@app.post("/process_document", summary="Process Document Image from URL")
async def process_document_image(
    url: str = Query(..., description="Presigned URL to the image file")
):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail=f"Failed to download image from URL. Status code: {response.status_code}")
        image_bytes = response.content
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"HTTP request failed: {e}"
        )

    try:
        structured_data = await process_image_to_structured_data(image_bytes)
        return structured_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to structure data from text: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during processing: {e}"
        )
