import fitz
import json
import io

def extract_text_from_pdf(file_bytes):
    try:
        doc = fitz.Document(stream=io.BytesIO(file_bytes), filetype="pdf")
        page_count = doc.chapter_page_count(0)
        extracted_text = []

        for page_num in range(page_count):
            load_page = doc.load_page(page_num)
            doc_response = json.loads(load_page.get_text("json", sort=True))
            for block in doc_response.get('blocks', []):
                for line in block.get('lines', []):
                    for span in line.get('spans', []):
                        extracted_text.append(span.get('text'))

        return "\n".join(extracted_text)

    except Exception as e:
        print(f"Error while processing pdf extracting as {e}")
        return ""  # always return a string
