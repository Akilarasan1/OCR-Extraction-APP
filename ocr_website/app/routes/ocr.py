# app/routes/ocr.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.image_ocr import tesseract, paddleocr # easyocr
from app.models.schemas import OCRResponse
from typing import List
from pathlib import Path
import tempfile
import shutil
import uuid
import os

router = APIRouter()

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "library" / "images"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/")
async def ocr_root():
    return {"message": "OCR endpoints available: /extract, /compare"}


@router.post("/extract", response_model=OCRResponse)
async def extract_text_from_image(
    file: UploadFile = File(...),
    engine: str = "paddleocr",
    lang: str = "en"
):
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded")

        max_size = 10 * 1024 * 1024  # 10MB
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        if file_size > max_size:
            raise HTTPException(status_code=413, detail="File too large")

        if "image" not in file.content_type:
            raise HTTPException(status_code=400, detail="Invalid image file")

        extension = Path(file.filename).suffix
        filename = f"{uuid.uuid4()}{extension}"
        image_path = (UPLOAD_DIR / filename).as_posix()

        with open(image_path, "wb") as out_file:
            shutil.copyfileobj(file.file, out_file)

        # OCR
        if engine == "paddleocr":
            text = paddleocr.extract_text_with_paddleocr([image_path], lang)
        elif engine == "tesseract":
            text = tesseract.extract_text_with_tesseract(image_path, lang)
            # print("text >>>>>>>>> ", type(text))

        else:
            raise HTTPException(status_code=400, detail="Invalid OCR engine")

        text = "\n".join(text) if isinstance(text, list) else str(text)

        return {
            "text": text,
            "engine": engine,
            "language": lang,
            "filename": file.filename,
            "status": "success"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OCR processing failed: {str(e)}")

    finally:
        if os.path.exists(image_path):
            os.remove(image_path)
