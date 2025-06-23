from isa.prototype.multi_modal_understanding.pdf_processor import extract_images_and_text_from_pdf
import os

class ExtractedImage:
    def __init__(self, name: str, path: str, ocr_text: str = "", original_bytes: bytes = None):
        self.name = name
        self.path = path
        self.ocr_text = ocr_text
        self.original_bytes = original_bytes # Optional: for direct image processing later

class ExtractedPage:
    def __init__(self, page_number: int, text: str = "", images: list = None):
        self.page_number = page_number
        self.text = text
        self.images = images if images is not None else []

class ExtractedDocument:
    def __init__(self, document_path: str, pages: list = None, raw_text: str = ""):
        self.document_path = document_path
        self.pages = pages if pages is not None else []
        self.raw_text = raw_text # For non-paged documents or aggregated text

def extract_content(document_path: str) -> ExtractedDocument:
    """
    Extracts content from various document types, including multi-modal data from PDFs.
    Returns a structured ExtractedDocument object.
    """
    print(f"Extracting content from {document_path}")
    file_extension = os.path.splitext(document_path)[1].lower()
    
    extracted_doc = ExtractedDocument(document_path=document_path)

    if file_extension == ".pdf":
        try:
            pdf_data = extract_images_and_text_from_pdf(document_path)
            for page_data in pdf_data:
                extracted_images = [
                    ExtractedImage(
                        name=img_info['name'],
                        path=img_info['path'],
                        ocr_text=img_info['ocr_text']
                    ) for img_info in page_data['images']
                ]
                extracted_doc.pages.append(
                    ExtractedPage(
                        page_number=page_data['page_number'],
                        text=page_data['text'],
                        images=extracted_images
                    )
                )
            # Aggregate all text for overall document context
            extracted_doc.raw_text = "\n".join([page.text for page in extracted_doc.pages])
            extracted_doc.raw_text += "\n".join([img.ocr_text for page in extracted_doc.pages for img in page.images])

        except Exception as e:
            print(f"Error processing PDF {document_path}: {e}")
            extracted_doc.raw_text = f"Error extracting content from PDF: {e}"
    elif file_extension in [".txt", ".md", ".html"]:
        with open(document_path, 'r', encoding='utf-8') as f:
            extracted_doc.raw_text = f.read()
    else:
        print(f"Unsupported document type: {file_extension}")
        extracted_doc.raw_text = f"Unsupported document type: {file_extension}"
    
    return extracted_doc