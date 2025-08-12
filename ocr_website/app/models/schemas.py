# app/models/schemas.py

from pydantic import BaseModel

class ExtractionResponse(BaseModel):
    text: str
    engine: str
    language: str
    filename: str
    file_type: str  # 'image', 'pdf', or 'scanned_pdf'
    status: str