from fastapi import FastAPI, HTTPException, status, Query
from models import Data
from services.ocr_service import process_image_to_structured_data
import os

app = FastAPI(
    title="OCR and Data Structuring Service",
    description="API for processing document images using Gemini and structuring extracted data."
)

@app.get("/health")
async def read_root():
    return {"message": "OCR Service is running. Go to /docs for API documentation."}

@app.post(
    "/process_document",
    response_model=Data,
    summary="Process Document Image and Extract Structured Data"
)
async def process_document_image(
    path: str = Query(..., description="Full path to image file inside the container, e.g., /data/uploads/sample.jpg")
):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"File not found at: {path}")

    try:
        with open(path, 'rb') as f:
            image_bytes = f.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not read image file at {path}: {e}"
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

