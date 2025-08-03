# main.py
from fastapi import FastAPI, File, UploadFile, HTTPException, status
from typing import Annotated
import io

from models import Data, ProcessedDocumentData
from services.ocr_service import process_image_to_structured_data 
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
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    import os
    from datetime import datetime
    
    # Check if required environment variables are present
    api_key_present = bool(os.getenv('GOOGLE_API_KEY'))
    
    return {
        "status": "healthy",
        "message": "OCR Service is running",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
        "environment": {
            "google_api_key_configured": api_key_present
        },
        "endpoints": {
            "docs": "/docs",
            "process_document": "/process_document"
        }
    }

@app.get("/")
async def read_root():
    return {"message": "OCR Service is running. Go to /docs for API documentation."}

@app.post(
    "/process_document",
    response_model=ProcessedDocumentData,  # Use the new response model
    summary="Process Document Image and Extract Structured Data"
)
@app.post("/process_document", summary="Process Document Image from URL")
async def process_document_image(
    url: str = Query(..., description="Presigned URL to the image file")
):

    """
    Receives a document image, performs OCR using Gemini, verifies the result,
    and structures the extracted text into a defined JSON format.
    """
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
    # # Read the image file bytes
    # try:
    #     image_bytes = await image.read()
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail=f"HTTP request failed: {e}"
    #     )

    try:
        structured_data = await process_image_to_structured_data(image_bytes)
        # Validate and serialize using the new model
        return ProcessedDocumentData.model_validate(structured_data)
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
