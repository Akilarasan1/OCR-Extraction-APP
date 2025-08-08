import pytesseract
import os
import shutil
from PIL import Image
import io

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


def extract_text_with_tesseract(file_img, lang = "en"):
    try:
        import cv2
        if find_tesseract_executable():
            # img = Image.open(file_img)
            # img = Image.open(stream=io.BytesIO(file_img), filetype=["jpg","png","jpeg"])
            # img_optimized = image_conversation.enhance_image(img)
            image = cv2.imread(file_img)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.bilateralFilter(gray, 11, 19, 19)  # smooth but keep edges
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            pil_image = Image.fromarray(cv2.cvtColor(gray, cv2.COLOR_BGR2RGB))
            custom_config = r'--oem 3 --psm 6'

            ocr_text = pytesseract.image_to_string(pil_image, lang='eng', config = custom_config)
            return ocr_text if ocr_text else None
        return None
    except Exception as e:
        print(f"Error processing Tesseract OCR: {e}")
        return None
