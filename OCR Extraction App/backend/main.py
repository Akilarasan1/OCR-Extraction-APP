from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from controller import read_img_pdf
from dotenv import load_dotenv


env_path = '.env'
load_dotenv(dotenv_path=env_path)

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or "*" for open access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your actual OCR endpoints
@app.post("/pytesseract_img")
async def pytesseract_img(request: Request):
    return await read_img_pdf.cloud_pytesseract(request)

@app.post("/paddle_ocr")
async def paddle_ocr(request: Request):
    return await read_img_pdf.cloud_paddleocr(request)

@app.post("/google_ocr_engine")
async def google_ocr_engine(request: Request):
    return await read_img_pdf.cloud_ocr_engine(request)

@app.post("/read_pdf_file")
async def read_pdf_file(request: Request):
    return await read_img_pdf.cloud_process_pdf(request)

# ✅ Dispatcher endpoint for React UI
@app.post("/route_selector")
async def route_selector(
    file_type: str = Form(...),
    engine: str = Form(...),
    file: UploadFile = File(...)):
    from starlette.requests import Request as StarletteRequest
    from starlette.datastructures import UploadFile as StarletteUploadFile
    from starlette.datastructures import FormData
    from starlette.requests import Request as StarletteRequest
    from fastapi import Request
    from starlette.testclient import TestClient

    # For internal request simulation
    client = TestClient(app)

    form_data = {'file_type': file_type, 'engine': engine}
    files = {'file': (file.filename, await file.read(), file.content_type)}

    # Decide target endpoint
    if file_type == "pdf":
        target_url = "/read_pdf_file"
    else:
        if engine == "pytesseract":
            target_url = "/pytesseract_img"
        elif engine == "paddle":
            target_url = "/paddle_ocr"
        elif engine == "google":
            target_url = "/google_ocr_engine"
        else:
            return JSONResponse({"error": "Invalid engine"}, status_code=400)

    response = client.post(target_url, files=files)
    return JSONResponse(content=response.json())
