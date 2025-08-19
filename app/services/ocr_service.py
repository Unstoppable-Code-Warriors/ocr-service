# app/services/ocr_service.py
import os
import io
import time
import asyncio
from dotenv import load_dotenv
from google import genai
from google.genai import types
from fastapi.concurrency import run_in_threadpool # To handle blocking API calls
import json
from PIL import Image
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

def preprocess_image(image_bytes: bytes, max_width: int = 1200, max_height: int = 1600) -> bytes:
    """
    Preprocess image to reduce size and improve OCR performance.
    - Resize to reasonable dimensions
    - Convert to grayscale (optional, but can speed up processing)
    - Compress to reduce file size
    """
    try:
        # Open image from bytes
        img = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary (handles RGBA, P mode, etc.)
        if img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')
        
        # Calculate new size maintaining aspect ratio
        width, height = img.size
        if width > max_width or height > max_height:
            # Calculate scaling factor
            scale_factor = min(max_width / width, max_height / height)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to grayscale to potentially speed up processing
        # Comment this line if you need color information
        # img = img.convert('L')
        
        # Save to bytes with optimized compression
        output_buffer = io.BytesIO()
        img.save(output_buffer, format='JPEG', quality=85, optimize=True)
        return output_buffer.getvalue()
        
    except Exception as e:
        print(f"Warning: Image preprocessing failed: {e}")
        # Return original image if preprocessing fails
        return image_bytes

async def perform_ocr_and_structure(image_bytes: bytes) -> ProcessedDocumentData:
    start_time = time.time()
    """Process image with Gemini Flash for OCR and direct structuring into ProcessedDocumentData model."""
    
    # Combined prompt for OCR and structuring in one API call
    prompt = """Analyze this document image and extract all information, then structure it into a JSON object.

    First, extract all text from the document:
    - For tables: keep structure in markdown, include headers and data accurately
    - For multi-column: process left to right, separate columns clearly  
    - Keep headers, footers, page numbers, and paragraph breaks
    
    Then, analyze the extracted content and structure it into a JSON object that matches the provided schema.
    Focus on identifying:
    - Patient information
    - Test codes and names
    - Results and values
    - Reference ranges
    - Dates and clinical information
    - Any hereditary cancer or genetic testing data
    
    Return only the structured JSON object."""

    try:
        # Use response_schema and response_mime_type to guide Gemini's output
        response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type='image/jpeg', # Or 'image/png', etc.
                    ),
                    prompt
                ],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": ProcessedDocumentData, 
                }
            )
        
        # Log số token nếu API hỗ trợ
        if hasattr(response, 'usage'):
            print(f"Tokens used: {response.usage.total_tokens}")
        
        # Pydantic will automatically parse the JSON response into the ProcessedDocumentData model
        structured_data: ProcessedDocumentData = response.parsed

        if structured_data is None:
            raise ValueError("Gemini returned no parsable structured data.")

        end_time = time.time()
        print(f"[perform_ocr_and_structure] Time taken: {end_time - start_time:.2f} seconds")
        return structured_data
    except Exception as e:
        print(f"Error during OCR and structuring: {e}")
        raise

async def perform_initial_ocr(image_bytes: bytes) -> str:
    start_time = time.time()
    """Process image with Gemini Flash for initial text extraction (OCR)."""
    
    # Preprocess image to reduce size and improve speed
    # processed_image = preprocess_image(image_bytes)
    
    # Simplified prompt for faster processing
    prompt = """Extract all text from this document page. 
    - For tables: keep structure in markdown, include headers and data accurately
    - For multi-column: process left to right, separate columns clearly  
    - Keep headers, footers, page numbers, and paragraph breaks
    Be accurate and complete."""

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
        # Log số token nếu API hỗ trợ
        if hasattr(response, 'usage'):
            print(f"Tokens used: {response.usage.total_tokens}")
        
        result = response.text
        end_time = time.time()
        print(f"[perform_initial_ocr] Time taken: {end_time - start_time:.2f} seconds")
        return result
    except Exception as e:
        print(f"Error during initial OCR: {e}")
        # Re-raise or handle appropriately
        raise

async def verify_ocr_text(image_bytes: bytes, extracted_text: str) -> str:
    start_time = time.time()
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
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type='image/jpeg',
                    ),
                    prompt
                ]
            )
        result = response.text # This text is the verification feedback/corrected text
        end_time = time.time()
        print(f"[verify_ocr_text] Time taken: {end_time - start_time:.2f} seconds")
        return result
    except Exception as e:
        print(f"Error during OCR verification: {e}")
        # Re-raise or handle appropriately
        raise


async def structure_data_from_text(processed_text: str):
    start_time = time.time()
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
                model="gemini-2.5-flash",
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

        end_time = time.time()
        print(f"[structure_data_from_text] Time taken: {end_time - start_time:.2f} seconds")
        return structured_data
    except Exception as e:
        print(f"Error structuring data from text: {e}")
        # Re-raise or handle appropriately
        raise


# Example combined function (called from FastAPI endpoint)
async def process_image_to_structured_data(image_bytes: bytes) -> ProcessedDocumentData:
    start_time = time.time()
    """Runs the optimized OCR and structuring pipeline in one API call."""
    
    # Use the new combined function that does OCR and structuring in one step
    structured_data = await perform_ocr_and_structure(image_bytes)

    end_time = time.time()
    print(f"[process_image_to_structured_data] Total pipeline time: {end_time - start_time:.2f} seconds")
    return structured_data