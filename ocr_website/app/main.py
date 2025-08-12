from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path

from .routes import ocr

app = FastAPI(redirect_slashes=False,
    title="Multi-Engine OCR Service",
    description="Service for text extraction from images and PDFs",
    version="1.0.0"
)

BASE_DIR = Path(__file__).resolve().parent
try:
    static_dir = BASE_DIR / "static"
    static_dir.mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
except Exception as e:
    print(f"Warning: Could not mount static files - {str(e)}")

try:
    templates_dir = BASE_DIR / "templates"
    templates = Jinja2Templates(directory=str(templates_dir))
except Exception as e:
    print(f"Warning: Could not configure templates - {str(e)}")
    templates = None


app.include_router(ocr.router, prefix="/api", tags=["Extraction"]) 
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    if not templates:
        return HTMLResponse(content="<h1>Server Error</h1><p>Templates not configured</p>", status_code=500)
    try:
        print("Rendering homepage...")
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        return HTMLResponse( content=f"<h1>Error from API </h1><p>{str(e)}</p>",status_code=500)
    

# app.include_router
    
