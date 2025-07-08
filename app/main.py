# main.py
from fastapi import FastAPI, File, UploadFile, HTTPException, status
from typing import Annotated
import io

from models import Data
from services.ocr_service import process_image_to_structured_data 

app = FastAPI(
    title="OCR and Data Structuring Service",
    description="API for processing document images using Gemini and structuring extracted data."
)

# Optional: Add a root endpoint for health check
@app.get("/health")
async def read_root():
    return {"message": "OCR Service is running. Go to /docs for API documentation."}

@app.post(
    "/process_document",
    # response_model=Data, # Indicate the successful response structure
    summary="Process Document Image and Extract Structured Data"
)
async def process_document_image(
    image: Annotated[UploadFile, File(description="Image file (JPG, PNG, etc.) to process.")]
):
    """
    Receives a document image, performs OCR using Gemini, verifies the result,
    and structures the extracted text into a defined JSON format.
    """
    if not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type. Please upload an image file."
        )

    # Read the image file bytes
    try:
        image_bytes = await image.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not read image file: {e}"
        )

    # Process the image using the service
    try:
        structured_data = await process_image_to_structured_data(image_bytes)
        return structured_data
    except ValueError as e:
         # Handle specific errors from the service (e.g., no parsable data)
         raise HTTPException(
             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, # Or 500 depending on cause
             detail=f"Failed to structure data from text: {e}"
         )
    except Exception as e:
        # Catch any other exceptions during the process
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during processing: {e}"
        )
