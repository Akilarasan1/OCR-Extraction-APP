import fitz
import json
def process_pdf_extract(file_path):
    try:
        doc = fitz.Document(file_path)
        table_doc = doc
        page_count = doc.chapter_page_count(0)
        response, doc_data = {}, []
        for page_num in range(page_count):
            load_page = doc.load_page(page_num)
            doc_response = json.loads(load_page.get_text("json", sort=True))
            pdf_data = []
            for data in doc_response.get('blocks'):
                lines = data.get('lines')
                if lines:
                    for text_line in lines:
                        for text_data in text_line.get('spans'):
                            pdf_data.append(text_data.get('text'))
        doc_data.append(pdf_data)
        return doc_data
    except Exception as e:
        print(f"Error while processing pdf extracting as {e}")
