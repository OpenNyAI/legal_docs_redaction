from docx_conversion.ConvertToDocx import ConvertToDocx
from redaction.spacy_redaction import DataRedaction
import os

if __name__ == "__main__":
    input_pdfs_folder = '/Users/prathamesh/tw_projects/OpenNyAI/data/LLM/Contracts for Review'
    docx_folder_path = input_pdfs_folder + '_docx'

    docx_converter = ConvertToDocx(input_pdfs_folder, docx_folder_path)
    docx_converter.convert_to_docx()

    redacted_output_path = docx_folder_path + '_redacted'
    n = DataRedaction(docx_folder_path, redacted_output_path)
    n.redact_all_files_in_folder()