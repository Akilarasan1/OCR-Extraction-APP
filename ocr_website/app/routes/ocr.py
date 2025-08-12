from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services import paddleocr
from app.models.schemas import ExtractionResponse
from pathlib import Path
import shutil
import uuid
import os
from typing import Union
import fitz  # PyMuPDF
from PIL import Image
import io
import logging
import json

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "library" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED_IMAGE_TYPES = ['.png', '.jpg', '.jpeg']
SUPPORTED_PDF_TYPE = '.pdf'

@router.post("/extract", response_model=ExtractionResponse)
async def extract_text(file: UploadFile = File(...),engine: str = "paddleocr",lang: str = "en"):
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        max_size = 10 * 1024 * 1024         # Check file size (10MB limit)
        contents = await file.read()
        if len(contents) > max_size:
            raise HTTPException(status_code=413, detail="File too large")
        extension = Path(file.filename).suffix.lower()

        if extension in SUPPORTED_IMAGE_TYPES:
            return await _process_image(contents, engine, lang, file.filename)
        elif extension == SUPPORTED_PDF_TYPE:
            return await _process_pdf(contents, engine, lang, file.filename)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500,detail=f"Extraction failed: {str(e)}")

async def _process_image(image_bytes: bytes,engine: str,lang: str,original_filename: str) -> ExtractionResponse:
    """Process image files with OCR"""
    try:
        temp_path = _save_temp_file(image_bytes, original_filename)
        if engine == "paddleocr":
            text = paddleocr.extract_text_with_paddleocr([temp_path], lang)
        else:
            raise HTTPException(status_code=400, detail="Invalid OCR engine")

        text = "\n".join(text) if isinstance(text, list) else str(text)

        return {
            "text": text,
            "engine": engine,
            "language": lang,
            "filename": original_filename,
            "file_type": "image",
            "status": "success"
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def extract_text_from_pdf(file_bytes):
    try:
        doc = fitz.Document(stream=io.BytesIO(file_bytes), filetype="pdf")
        page_count = doc.chapter_page_count(0)
        data, extracted_text = None,[]

        for page_num in range(page_count):
            load_page = doc.load_page(page_num)
            doc_response = json.loads(load_page.get_text("json", sort=True))
            for block in doc_response.get('blocks', []):
                for line in block.get('lines', []):
                    for span in line.get('spans', []):
                        extracted_text.append(span.get('text'))

        data = "\n".join(extracted_text) if extracted_text else None
        return data

    except Exception as e:
        print(f"Error while processing pdf extracting as {e}")
        return None  # always return a string

async def _process_pdf(pdf_bytes: bytes,engine: str,lang: str,original_filename: str) -> ExtractionResponse:
    """Process PDF files, including scanned PDFs"""
    try:
        try:
            text = extract_text_from_pdf(pdf_bytes)
            if not text: # If regular extraction fails, treat as scanned PDF
                return await _process_scanned_pdf(pdf_bytes, engine, lang, original_filename)
            return {
                "text": text,
                "engine": "pdfminer",
                "language": lang,
                "filename": original_filename,
                "file_type": "pdf",
                "status": "success"
            }
        

        except Exception as pdf_error:
            logger.info(f"Regular PDF extraction failed, trying scanned PDF: {str(pdf_error)}")
            

            # return await _process_scanned_pdf(pdf_bytes, engine, lang, original_filename)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF processing failed: {str(e)}"
        )

async def _process_scanned_pdf(pdf_bytes: bytes,engine: str,lang: str,original_filename: str) -> ExtractionResponse:
    """Process scanned PDF by converting pages to images"""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        full_text = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("png")
            page_text = await _process_image(img_bytes, engine, lang, f"{original_filename}_page{page_num+1}")
            full_text.append(page_text["text"])

        return {
            "text": "\n\n".join(full_text),
            "engine": engine,
            "language": lang,
            "filename": original_filename,
            "file_type": "scanned_pdf",
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Scanned PDF processing failed: {str(e)}")

def _save_temp_file(file_bytes: bytes,original_filename: str) -> str:
    """Save temporary file and return path"""
    extension = Path(original_filename).suffix.lower()
    filename = f"{uuid.uuid4()}{extension}"
    temp_path = (UPLOAD_DIR / filename).as_posix()
    
    with open(temp_path, "wb") as f:
        f.write(file_bytes)
    
    return temp_path