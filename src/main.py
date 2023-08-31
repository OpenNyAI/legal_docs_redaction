from docx_conversion.ConvertToDocx import ConvertToDocx
from redaction.spacy_redaction import DataRedaction
import os

if __name__ == "__main__":
    input_pdfs_folder = '/Users/prathamesh/tw_projects/OpenNyAI/data/LLM/Contracts for Review'
    text_folder_path = os.path.join(input_pdfs_folder, 'output', 'text')

    docx_converter = ConvertToDocx(input_pdfs_folder, text_folder_path)
    docx_converter.convert_to_docx()

    redacted_output_path = os.path.join(input_pdfs_folder, 'output', 'text','redacted')
    n = DataRedaction(text_folder_path, redacted_output_path)
    n.redact_all_files_in_folder()