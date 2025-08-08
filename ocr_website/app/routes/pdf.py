# app/routes/pdf.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pdf_extractor import extract_text_from_pdf
from app.models.schemas import PDFResponse

router = APIRouter()

@router.post("/extract", response_model=PDFResponse)
async def extract_text_from_pdf_file(file: UploadFile = File(...)):
    """Extract text from PDF file"""
    try:
        pdf_bytes = await file.read()
        text = extract_text_from_pdf(pdf_bytes)
        response = {"status": 'success', "text": text, "filename": file.filename}
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))