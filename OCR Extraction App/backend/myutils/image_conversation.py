from PIL import Image,ImageEnhance
import numpy as np
import cv2
import random
import traceback
import os
import io

def set_image_dpi(file_path):
    im = Image.open(file_path) 
    length_x, width_y = im.size
    factor = min(1, float(1024.0 / length_x))
    size = int(factor * length_x), int(factor * width_y)
    im_resized = im.resize(size, Image.Resampling.LANCZOS)
    return im_resized


def adjust_brightness_contrast(image, brightness=1.0, contrast=1.5):
    """Adjust the brightness and contrast of the image dynamically."""
    enhancer_brightness = ImageEnhance.Brightness(image)
    image = enhancer_brightness.enhance(brightness) 
    enhancer_contrast = ImageEnhance.Contrast(image)
    image = enhancer_contrast.enhance(contrast)
    return image


def enhance_image(image_path,convert_to_bw=True):
    try:
        """Preprocess the image to enhance readability for OCR."""
        
        # image = Image.open(image_path)
        image = adjust_brightness_contrast(image_path, brightness = 1.9, contrast = 1.0)
        if convert_to_bw:
            image = image.convert("L") 
            image = np.array(image)
            image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 11, 3)
        else:
            """Preprocess the image to enhance readability for OCR."""
            image = set_image_dpi(image_path)
            image = adjust_brightness_contrast(image, brightness =1.0, contrast = 1.0)
            image = image.convert("L") 
            image = np.array(image)
            if image.dtype != np.uint8:
                image = image.astype(np.uint8)

            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
            image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
            kernel = np.zeros((6,6),np.uint8)
            image = cv2.erode(image, kernel, iterations = 1)
            image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 2 )
            image = cv2.normalize(image, image, 0,255,cv2.NORM_MINMAX)
            
            image = cv2.bilateralFilter(image, 9, 89, 89)
           

        file_path = 'images/'+str(random.randint(0,999))+'enhanced'+'.png'
        content = os.path.abspath(file_path)
        cv2.imwrite(content, image)
        return content
    
    except Exception:
        print('::::: Exception occurred while process enhance image :::::')
        print(traceback.format_exc())
        return image_path