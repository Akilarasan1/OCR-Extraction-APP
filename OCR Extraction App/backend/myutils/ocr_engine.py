from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from google.oauth2 import service_account
from google.cloud import vision
import os
import io
import traceback
import pytesseract
import shutil
from paddleocr import PaddleOCR

async def ocr_process(file_name):
    try:
        data_sep, annotations = [], []
        key_path = os.getenv('json_file_path')
        if not key_path or not os.path.exists(key_path):
            raise FileNotFoundError("Service account JSON file not found")

        credentials = service_account.Credentials.from_service_account_file(
            key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

        client = vision.ImageAnnotatorClient(credentials=credentials)
        with io.open(file_name, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        ocr_response = client.document_text_detection(image=image)
        annotations = ocr_response.text_annotations
        if annotations:
            text = annotations[0].description
            parsed_text = text.replace("\n", ",").split(",")
            data_sep = parsed_text

        return data_sep, annotations
    
    except Exception:
        print("::::: Exception occurred while processing OCR :::::")
        print(traceback.format_exc())
        return data_sep, annotations
    
def find_tesseract_executable():
    """
    Check if Tesseract is installed and set its path.
    Returns True if found, otherwise raises an exception.
    """
    tesseract_path = shutil.which("tesseract")
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        return True

    tesseract_env_path = os.getenv("TESSERACT_PATH")
    if tesseract_env_path and os.path.exists(tesseract_env_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_env_path
        return True

    common_paths = [
        os.path.expanduser("~\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe")]
    for path in common_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            return True

    raise FileNotFoundError("Tesseract executable not found. Please install Tesseract OCR or set TESSERACT_PATH environment variable.")




    
    