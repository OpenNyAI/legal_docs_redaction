from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import deepdoctection as dd
import glob
import os
import pdfplumber
import pdf2image
import pytesseract
from joblib import Parallel, delayed
from tqdm import tqdm

def build_deepdoctection_analyzer():
    # experiment_name = '_table_transformer'
    # config_overwrite = ["PT.LAYOUT.WEIGHTS=microsoft/table-transformer-detection/pytorch_model.bin",
    #                     "USE_TABLE_SEGMENTATION=True",
    #                     "PT.LAYOUT.PAD.TOP=1",
    #                     "PT.LAYOUT.PAD.RIGHT=1",
    #                     "PT.LAYOUT.PAD.BOTTOM=1",
    #                     "PT.LAYOUT.PAD.LEFT=1"]
    #
    #
    # analyzer = dd.get_dd_analyzer(config_overwrite = config_overwrite)

    experiment_name = '_residual_text_container'
    config_overwrite = ["USE_LAYOUT=True","USE_TABLE_SEGMENTATION=True","USE_TABLE_REFINEMENT=True","TEXT_ORDERING.INCLUDE_RESIDUAL_TEXT_CONTAINER=True"]


    # config_overwrite = ["USE_LAYOUT=False","USE_TABLE_SEGMENTATION=False","USE_TABLE_REFINEMENT=False"]
    analyzer = dd.get_dd_analyzer(config_overwrite=config_overwrite)
    return analyzer
def convert_pdf_to_text_ocr_with_layout_detection(analyzer, input_pdf_path,annotated_pdf_path)->str:
    df = analyzer.analyze(path=input_pdf_path)
    df.reset_state()

    doc = iter(df)

    doc_text = ''
    pp = PdfPages(annotated_pdf_path)

    for i,page in enumerate(doc):
        fig = plt.figure(figsize=(25,17))
        plt.axis('off')
        plt.imshow(page.viz())

        pp.savefig(fig)
        plt.close(fig)
        doc_text += page.text
        if i > 10:
            break
    pp.close()
    return doc_text

def extract_text_without_ocr(input_pdf_path) -> str:
    with pdfplumber.open(input_pdf_path) as pdf:
        doc_text = ''
        for page in pdf.pages:
            doc_text += page.extract_text()
    return doc_text


def get_images_from_pdf(file_path: str, dpi: int = 200, fmt: str = 'png', thread_count: int = 1) -> list:
    return pdf2image.convert_from_path(file_path, dpi=dpi, fmt=fmt, thread_count=thread_count)
def extract_text_from_image(image_bytes, custom_oem_psm_config=r'--psm 6 -c preserve_interword_spaces=1',
                            lang="eng"):
    return pytesseract.image_to_string(image_bytes, lang=lang, config=custom_oem_psm_config)

def convert_pdf_to_text_ocr(pdf_path,lang = 'eng') -> str:
    pdf_text = ''
    pdf_images = get_images_from_pdf(pdf_path)
    for image in pdf_images:
        text = extract_text_from_image(image,lang=lang)
        pdf_text += text
    return pdf_text

def convert_pdf_to_text_hybrid_and_write(file_path,output_text_folder_path) -> str:
    doc_text = extract_text_without_ocr(file_path)
    if doc_text == '':
        doc_text = convert_pdf_to_text_ocr(file_path)
    output_text_file_path = os.path.join(output_text_folder_path, os.path.basename(file_path).replace('.pdf', '.txt'))
    with open(output_text_file_path, 'w') as f:
        f.write(doc_text)



if __name__ == '__main__':
    experiment_name = '_plain_ocr'
    input_pdfs_folder = '/Users/prathamesh/tw_projects/OpenNyAI/data/LLM/Contracts for Review'
    output_text_folder_path = os.path.join(input_pdfs_folder,'output','text'+experiment_name)
    os.makedirs(output_text_folder_path,exist_ok=True)

    # Option 1. Plain OCR without layout detection
    Parallel(n_jobs=-1)(
        delayed(convert_pdf_to_text_hybrid_and_write)(path,output_text_folder_path) for path in tqdm(glob.glob(input_pdfs_folder+ '/*.pdf')))

    # Option 2. OCR with layout detection
    # experiment_name = '_layout_detection
    # annotated_pdf_folder_path = os.path.join(input_pdfs_folder,'output','annotated'+experiment_name)
    # os.makedirs(annotated_pdf_folder_path,exist_ok=True)
    # analyzer = build_deepdoctection_analyzer()
    # annotated_pdf_path = os.path.join(annotated_pdf_folder_path,os.path.basename(file_path))
    # for file_path in tqdm(glob.glob(input_pdfs_folder+ '/*.pdf')):
        # doc_text = convert_pdf_to_text_ocr_with_layout_detection(analyzer,file_path,annotated_pdf_path)
        # output_text_file_path = os.path.join(output_text_folder_path, os.path.basename(file_path).replace('.pdf', '.txt'))
        # with open(output_text_file_path, 'w') as f:
        #     f.write(doc_text)



