from paddleocr import PaddleOCR
import gc
from wand.image import Image
from wand.color import Color
from concurrent.futures import ThreadPoolExecutor
import os
from wand.exceptions import MissingDelegateError, WandException
from pathlib import Path

def get_y_range(box):
    y_values = [pt[1] for pt in box]
    return min(y_values), max(y_values)

def get_x(box):
    return box[0][0] 

def process_coordinates(sep_ext):
    try:
        page_data = [] 
        for page_no in sep_ext:            
            text_boxes = []
            for box_coords, (text, _) in page_no:
                y_min, y_max = get_y_range(box_coords)
                y_center = (y_min + y_max) / 2
                x_start = get_x(box_coords)
                box_height = y_max - y_min
                text_boxes.append({
                    "y_center": y_center,
                    "x": x_start,
                    "size": box_height,
                    "description": text})
            text_boxes.sort(key=lambda b: b["y_center"])
        
            current_line = []
            last_y = None
            threshold = 12
            for box in text_boxes:
                if last_y is None or abs(box["y_center"] - last_y) < threshold:
                    current_line.append(box)
                else:
                    current_line.sort(key=lambda b: b["x"])
                    line_text = " ".join(b["description"] for b in current_line)
                    page_data.append(line_text) 
                    current_line = [box]
                last_y = box["y_center"]
    
            if current_line:
                current_line.sort(key=lambda b: b["x"])
                line_text = " ".join(b["description"] for b in current_line)
                page_data.append(line_text)  
        return page_data
    except Exception as e:
        print(f"error while processing coordinates sort data >>>>>>> {e}")



def extract_text_with_paddleocr(image_paths, lang ='en'):
    try:
        ocr = PaddleOCR(use_angle_cls=True, lang=lang, use_mp=True, show_log=False)
        result = None
        if isinstance(image_paths, str):
            result = ocr.ocr(str(image_paths), cls=True)
            final_data = process_coordinates(result)

            if isinstance(final_data, list):
                return "\n".join(final_data)
            else:
                return str(final_data)

    except Exception as e:
        print(f'while Error Processing paddle_ocr image processing:::: {e}')
        pass
 
