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
        all_pages_data = []  
        for page_no in sep_ext:
            page_data = []
            for page in page_no:
                text_boxes = []
                for box_coords, (text, _) in page:
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
            all_pages_data.append(page_data) 
        return all_pages_data
    except Exception as e:
        print(f"error while processing coordinates sort data >>>>>>> {e}")

def coordinates_mid_sort():
    return None


def extract_text_with_paddleocr(image_paths, lang ='en'):
    try:
        ocr = PaddleOCR(use_angle_cls=True, lang=lang, use_mp=True, show_log=False)
        all_pages_data = []
        if isinstance(image_paths, str):
            image_paths = [image_paths]

        for img_path in image_paths:
            with Image(filename=img_path, resolution=300) as img:
                img.background_color = Color("white")
                img.alpha_channel = "remove"

                for i, page in enumerate(img.sequence):
                    with Image(page) as single_page:
                        single_page.background_color = Color("white")
                        single_page.alpha_channel = "remove"

                        tmp_path = Path(__file__).resolve().parents[2] / "library" / "images"
                        tmp_path.mkdir(exist_ok=True, parents=True)
                        path_image = tmp_path / f"test_page_{i}.png"
                        single_page.save(filename=path_image)

                        result = ocr.ocr(str(path_image), cls=True)
                        if os.path.exists(path_image):
                            os.remove(path_image)
                        all_pages_data.append(result)

        final_data = process_coordinates(all_pages_data)
        if isinstance(final_data, list):
            flattened = [item for sublist in final_data for item in sublist]
            return "\n".join(flattened)
        else:
            return str(final_data)

    except Exception as e:
        print(f'while Error Processing paddle_ocr image processing:::: {e}')
        pass
    finally:
        gc.collect()
        for path in image_paths:

            if os.path.exists(path):
                os.remove(path)
