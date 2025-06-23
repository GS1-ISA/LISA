import os
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
import io

# Ensure Tesseract is installed and its path is set if not in PATH
# pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract' # Example for macOS

def extract_images_and_text_from_pdf(pdf_path, output_dir="extracted_content"):
    """
    Extracts images and text from each page of a PDF and performs OCR on images.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    reader = PdfReader(pdf_path)
    num_pages = len(reader.pages)

    extracted_data = []

    for i, page in enumerate(reader.pages):
        page_data = {"page_number": i + 1, "text": "", "images": []}

        # Extract text
        page_text = page.extract_text()
        if page_text:
            page_data["text"] = page_text
        
        # Extract images (this extracts raw image objects, not necessarily rendered content)
        # For a true visual extraction, rendering PDF pages to images is often required.
        # This part is a placeholder for more advanced image extraction.
        for image_file_object in page.images:
            try:
                image_name = image_file_object.name
                image_bytes = image_file_object.data
                image_path = os.path.join(output_dir, f"page_{i+1}_{image_name}")
                
                with open(image_path, "wb") as fp:
                    fp.write(image_bytes)
                
                # Perform OCR on the extracted image
                img = Image.open(io.BytesIO(image_bytes))
                ocr_text = pytesseract.image_to_string(img)
                
                page_data["images"].append({
                    "name": image_name,
                    "path": image_path,
                    "ocr_text": ocr_text
                })
            except Exception as e:
                print(f"Could not process image on page {i+1}: {e}")

        extracted_data.append(page_data)
    
    return extracted_data

if __name__ == "__main__":
    # This is a placeholder for a sample PDF.
    # You would need to provide a PDF file for testing.
    # For example, place a PDF named 'sample_document.pdf' in the same directory.
    sample_pdf_path = "GS1-Style-Guide.pdf"
    output_directory = "extracted_content"

    if os.path.exists(sample_pdf_path):
        print(f"Processing {sample_pdf_path}...")
        data = extract_images_and_text_from_pdf(sample_pdf_path, output_directory)
        for page in data:
            print(f"\n--- Page {page['page_number']} ---")
            print("Text:")
            print(page["text"][:500] + "..." if len(page["text"]) > 500 else page["text"])
            print("Images:")
            for img_info in page["images"]:
                print(f"  - Image: {img_info['name']}, Path: {img_info['path']}")
                print(f"    OCR Text: {img_info['ocr_text'][:200]}..." if len(img_info['ocr_text']) > 200 else img_info['ocr_text'])
    else:
        print(f"Error: {sample_pdf_path} not found. Please provide a sample PDF for testing.")
        print("You can create a dummy PDF or place an existing one in the 'isa/prototype/multi_modal_understanding/' directory.")