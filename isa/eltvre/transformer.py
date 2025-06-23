from .extractor import ExtractedDocument, ExtractedPage, ExtractedImage

def transform_data(extracted_doc: ExtractedDocument) -> ExtractedDocument:
    """
    Transforms the ExtractedDocument, performing text cleaning, normalization,
    and potentially entity recognition on text and OCR content.
    """
    print(f"Transforming content from {extracted_doc.document_path}")
    # Placeholder for actual transformation logic
    # For now, it just passes through, but future implementations will process
    # extracted_doc.raw_text, extracted_doc.pages[x].text, and extracted_doc.pages[x].images[y].ocr_text

    # Example: simple text normalization (can be expanded)
    if extracted_doc.raw_text:
        extracted_doc.raw_text = extracted_doc.raw_text.strip().lower()
    
    for page in extracted_doc.pages:
        if page.text:
            page.text = page.text.strip().lower()
        for image in page.images:
            if image.ocr_text:
                image.ocr_text = image.ocr_text.strip().lower()

    return extracted_doc