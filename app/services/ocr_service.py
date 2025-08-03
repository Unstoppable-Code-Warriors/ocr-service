# app/services/ocr_service.py
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from fastapi.concurrency import run_in_threadpool # To handle blocking API calls
import json
from models import Data,ProcessedDocumentData # Import the Pydantic model

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")

# Initialize Gemini Client once
# It's generally safe to initialize the client globally in FastAPI
# as long as it doesn't hold user-specific state.
try:
    client = genai.Client(api_key=api_key)
    # Optional: Test connection
    # print("Gemini client initialized successfully.")
except Exception as e:
    print(f"Error initializing Gemini client: {e}")
    # Depending on severity, you might want to raise the exception
    # or have a health check endpoint.

async def perform_initial_ocr(image_bytes: bytes) -> str:
    """Process image with Gemini Flash for initial text extraction (OCR)."""
    prompt = """
    
    Extract ALL text content from this document page.
    For tables:
    1. Maintain the table structure using markdown table format
    2. Preserve all column headers and row labels
    3. Ensure numerical data is accurately captured
    
    For multi-column layouts:
    1. Process columns from left to right
    2. Clearly separate content from different columns
    
    For charts and graphs:
    1. Describe the chart type
    2. Extract any visible axis labels, legends, and data points
    3. Extract any title or caption
    
    Preserve all headers, footers, page numbers, and footnotes.
    Maintain paragraph breaks and formatting.
    Be as accurate as possible.
    """

    # Gemini's sync client methods need to be run in a thread pool
    # to avoid blocking the FastAPI async event loop.
    try:
        response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type='image/jpeg', # Or 'image/png', etc.
                    ),
                    prompt
                ]
            )
        return response.text
    except Exception as e:
        print(f"Error during initial OCR: {e}")
        # Re-raise or handle appropriately
        raise

async def verify_ocr_text(image_bytes: bytes, extracted_text: str) -> str:
    """Verify the quality of OCR results against the original image."""
    prompt = f"""
    I have a document page and text that was extracted from it using OCR.

    Compare the original image with the extracted text and identify any significant errors or omissions.
    Focus on:
    - Missing text sections or paragraphs.
    - Major incorrect words or numbers.
    - Obvious table or list structure issues if present.

    Report back the *verified* or *corrected* text if significant errors were found, or confirm if it looks accurate.

    Extracted text:
    {extracted_text}
    """

    try:
        response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type='image/jpeg',
                    ),
                    prompt
                ]
            )
        return response.text # This text is the verification feedback/corrected text
    except Exception as e:
        print(f"Error during OCR verification: {e}")
        # Re-raise or handle appropriately
        raise


async def structure_data_from_text(processed_text: str):
    """
    Based on the processed text (potentially verified/corrected OCR),
    ask Gemini to structure the information into the Data Pydantic model.
    """
    prompt = f"""
    Based on the following text extracted from a document page,
    extract the key information and structure it into a JSON object
    that conforms to the provided schema.

    Text:
    {processed_text}
    """

    try:
        # Use response_schema and response_mime_type to guide Gemini's output
        response = client.models.generate_content(
                contents=[prompt],
                model="gemini-2.0-flash",
                config={
                    "response_mime_type": "application/json",
                    "response_schema": ProcessedDocumentData, 
                },
            )
        # print(response)
        # Pydantic will automatically parse the JSON response into the Data model
        # when using response_schema with the client.
        structured_data: ProcessedDocumentData = response.parsed # Access the parsed model

        if structured_data is None:
             # This can happen if Gemini returns non-parsable JSON or an empty response
             raise ValueError("Gemini returned no parsable structured data.")

        return structured_data

    except Exception as e:
        print(f"Error structuring data from text: {e}")
        # Re-raise or handle appropriately
        raise


# Example combined function (called from FastAPI endpoint)
async def process_image_to_structured_data(image_bytes: bytes) -> Data:
    """Runs the full OCR, verification, and structuring pipeline."""
    raw_ocr_text = await perform_initial_ocr(image_bytes)

    # Optional: You could choose to use the raw text directly for structuring
    # verified_text = raw_ocr_text
    # Or use the verification step's output as the source for structuring
    verification_feedback = await verify_ocr_text(image_bytes, raw_ocr_text)
    verified_text = verification_feedback # Using verification feedback as source text

    # Use the (potentially corrected/verified) text to structure the data
    structured_data = await structure_data_from_text(verified_text)

    return structured_data