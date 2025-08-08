# app/models/schemas.py
from pydantic import BaseModel
class OCRResponse(BaseModel):
    text: str
    engine: str
    language: str
    filename: str
    status: str

class PDFResponse(BaseModel):
    status: str
    text: str
    filename: str
