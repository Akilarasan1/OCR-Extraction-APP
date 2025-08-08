# app/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path

from .routes import ocr, pdf

app = FastAPI(title="Multi-Engine OCR Service")

# Mount static files and templates
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


app.include_router(ocr.router, prefix="/api/ocr", tags=["OCR"])
app.include_router(pdf.router, prefix="/api/pdf", tags=["PDF"])

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    print("Rendering homepage...")
    return templates.TemplateResponse("index.html", {"request": request})
