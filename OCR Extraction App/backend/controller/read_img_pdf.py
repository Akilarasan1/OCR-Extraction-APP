from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from logic import paddleocr, pytesseract,pdf_extract
from myutils.ocr_engine import ocr_process
from starlette.datastructures import UploadFile
import os
import random


async def cloud_pytesseract(request: Request):
    
    try:
        form = await request.form()
        uploaded_file = form.get("file")
        image_paths = await process_upload_file(uploaded_file)
        images = pytesseract.process_tesseract(image_paths)
        return JSONResponse(content={"message": "success", "results": images}, status_code=200)

    except Exception as e:
        print(f"Error in cloud_paddleocr: {e}")
        return JSONResponse(
            content={"message": "An error occurred during processing.", "messageType": "E"},
            status_code=500
        )


async def cloud_paddleocr(request: Request):
    try:
        form = await request.form()
        uploaded_file = form.get("file")
        image_paths = await process_upload_file(uploaded_file)
        result = paddleocr.process_paddle_ocr(image_paths) 
        return JSONResponse(content={"message": "success", "results": result}, status_code=200)

    except Exception as e:
        print(f"Error in cloud_paddleocr: {e}")
        return JSONResponse(
            content={"message": "An error occurred during processing.", "messageType": "E"},
            status_code=500)
    
async def cloud_ocr_engine(request: Request):
    try:
        form = await request.form()
        uploaded_file = form.get("file")
        image_paths = await process_upload_file(uploaded_file)
        result,_ = ocr_process(image_paths) # "result" contains list of data,"_" - data coordinates, if we want aligned data we can use it
        return JSONResponse(content={"message": "success", "results": result}, status_code=200)

    except Exception as e:
        print(f"Error in Google_ocr_engine: {e}")
        return JSONResponse(
            content={"message": "An error occurred during processing.", "messageType": "E"},
            status_code=500)

async def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

async def cloud_process_pdf(request: Request):
    try:
        form = await request.form()
        uploaded_file: UploadFile = form.get("file")
        
        if not uploaded_file or not await allowed_file(uploaded_file.filename):
            return JSONResponse(
                content={"message": "Please attach a valid PDF file to proceed.", "messageType": "E"},
                status_code=400
            )

        n = random.randint(0, 999)
        data_file_path = f"images/{n}_{uploaded_file.filename}"
        with open(data_file_path, "wb") as f:
            f.write(await uploaded_file.read())
        image_data = pdf_extract.process_pdf_extract(data_file_path)
        os.remove(data_file_path)
        return JSONResponse(content={"message": "success", "results": image_data}, status_code=200)

    except Exception as e:
        print(f"Error in fitz library: {e}")
        return JSONResponse(
            content={"message": "An error occurred during processing.", "messageType": "E"},
            status_code=500
        )


async def process_upload_file(uploaded_file):
    try:
        if uploaded_file is None:
            raise HTTPException(status_code=400, detail="No file uploaded")

        images_dir = "images"
        os.makedirs(images_dir, exist_ok=True)

        filename = uploaded_file.filename
        extension = filename.split('.')[-1].lower()
        temp_file_path = os.path.join(images_dir, filename)

        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(await uploaded_file.read())
        return [temp_file_path] 

    except Exception as e:
        print("Error in process_upload_file:", e)
        raise HTTPException(status_code=500, detail=str(e))


    except FileNotFoundError as e:
        return JSONResponse(content={"error": str(e)}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
