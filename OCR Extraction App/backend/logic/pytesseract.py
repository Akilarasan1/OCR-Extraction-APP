import pytesseract
from myutils.ocr_engine import find_tesseract_executable
from PIL import Image
from myutils import image_conversation

def process_tesseract(file_img):
    try:
        if find_tesseract_executable():
            img = Image.open(file_img)
            img_optimized = image_conversation.enhance_image(img)
            text = pytesseract.image_to_string(img_optimized,lang='eng')
            text = text.split('\n')
            print("text>>>>>>>>>>> ", text)
            return text if text else None
        return None
    except Exception as e:
        print(f"Error processing Tesseract OCR: {e}")
        return None
