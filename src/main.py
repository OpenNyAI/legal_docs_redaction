from ConvertToDocx import ConvertToDocx
from spacy_redaction import DataRedaction
import os

if __name__ == "__main__":
    input_pdfs_folder = '/Users/prathamesh/tw_projects/OpenNyAI/data/LLM/data_readaction/test'
    output_folder_path = '/Users/prathamesh/tw_projects/OpenNyAI/data/LLM/data_readaction/test_output'

    # input_pdfs_folder = '/data/input'
    # output_folder_path = '/data/output'

    docx_folder_path = os.path.join(output_folder_path, 'docx')
    docx_converter = ConvertToDocx(input_pdfs_folder, docx_folder_path)
    docx_converter.convert_to_docx()

    redacted_output_path = os.path.join(output_folder_path ,'redacted')
    n = DataRedaction(docx_folder_path, redacted_output_path)
    n.redact_all_files_in_folder()