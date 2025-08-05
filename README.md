Project Title: OCR EXTRACTION APP with File Upload and Engine Selector

✅ What I Built
I created an OCR (Optical Character Recognition) web application using FastAPI (Python) for the backend and ReactJS for the frontend.

The app lets users:

Upload image or PDF files

Choose the OCR engine (like Pytesseract, PaddleOCR, or Google Vision API)

Extract the text from the uploaded files

View the result on the screen

🔧 Technologies I Used
FastAPI – for creating the API endpoints

ReactJS – for the frontend UI

Pytesseract, PaddleOCR, Google OCR – to extract text from images and PDFs

HTML/CSS + JS – used inside the React components

Axios – to connect React with FastAPI

CORS – to allow frontend and backend to communicate

🔁 How It Works
User selects:

File Type: PDF or Image

OCR Engine: Pytesseract / Paddle / Google

Uploads a file

Based on selection, the file is sent to the correct backend API:

For PDFs: /read_pdf_file

For images:

/pytesseract_img

/paddle_ocr

/google_ocr_engine

OCR is performed on the backend

Extracted text is returned and shown on the webpage

💡 Why I Built This
I wanted to make it easy for non-technical users to extract text from documents

I also wanted to learn how to build a full-stack app using React and FastAPI

I focused on learning file upload handling, API routing, and React integration
