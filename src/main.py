from pdf_to_text.OCR import OCR
from redaction.spacy_redaction import DataRedaction
import os

if __name__ == "__main__":
    input_pdfs_folder = '/Users/prathamesh/tw_projects/OpenNyAI/data/LLM/Contracts for Review'
    text_folder_path = os.path.join(input_pdfs_folder, 'output', 'text')

    ocr = OCR(input_pdfs_folder,text_folder_path)
    ocr.perform_ocr()

    redacted_output_path = os.path.join(input_pdfs_folder, 'output', 'text','redacted')
    n = DataRedaction(text_folder_path, redacted_output_path)
    n.redact()