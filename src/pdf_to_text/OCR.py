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


class OCR:
    def __init__(self,input_pdfs_folder,output_text_folder_path):
        self.input_pdfs_folder = input_pdfs_folder
        self.output_text_folder_path = output_text_folder_path

        os.makedirs(output_text_folder_path, exist_ok=True)

        self.use_layout_detection = False # If false then plain tesseract would be used. Else layout detection is done
        self.model_for_layout_detection = 'detectron2' # 'table-transformer' or 'detectron2'

        if self.use_layout_detection:
            self.annotated_pdf_folder_path = os.path.join(output_text_folder_path, 'annotated')
            os.makedirs(self.annotated_pdf_folder_path, exist_ok=True)

    def _build_deepdoctection_analyzer(self):
        config_overwrite = ["USE_LAYOUT=False",
                            "USE_TABLE_SEGMENTATION=False",
                            "USE_TABLE_REFINEMENT=False"]

        if self.use_layout_detection:
            if self.model_for_layout_detection == 'table-transformer':
                # Run pip install deepdoctection[pt]
                config_overwrite = ["PT.LAYOUT.WEIGHTS=microsoft/table-transformer-detection/pytorch_model.bin",
                                    "USE_TABLE_SEGMENTATION=True",
                                    "PT.LAYOUT.PAD.TOP=1",
                                    "PT.LAYOUT.PAD.RIGHT=1",
                                    "PT.LAYOUT.PAD.BOTTOM=1",
                                    "PT.LAYOUT.PAD.LEFT=1"]

            elif self.model_for_layout_detection == 'detectron2':
                config_overwrite = ["USE_LAYOUT=True",
                                    "USE_TABLE_SEGMENTATION=True",
                                    "USE_TABLE_REFINEMENT=True",
                                    "TEXT_ORDERING.INCLUDE_RESIDUAL_TEXT_CONTAINER=True"]

        analyzer = dd.get_dd_analyzer(config_overwrite=config_overwrite)
        return analyzer
    def _convert_pdf_to_text_ocr_with_layout_detection(self,analyzer, input_pdf_path,annotated_pdf_path)->str:
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

    def _extract_text_without_ocr(self,input_pdf_path) -> str:
        with pdfplumber.open(input_pdf_path) as pdf:
            doc_text = ''
            for page in pdf.pages:
                doc_text += page.extract_text()
        return doc_text


    def _get_images_from_pdf(self,file_path: str, dpi: int = 200, fmt: str = 'png', thread_count: int = 1) -> list:
        return pdf2image.convert_from_path(file_path, dpi=dpi, fmt=fmt, thread_count=thread_count)
    def _extract_text_from_image(self,image_bytes, custom_oem_psm_config=r'--psm 6 -c preserve_interword_spaces=1',
                                lang="eng"):
        return pytesseract.image_to_string(image_bytes, lang=lang, config=custom_oem_psm_config)

    def _convert_pdf_to_text_ocr(self,pdf_path,lang = 'eng') -> str:
        if self.use_layout_detection:
            analyzer = self._build_deepdoctection_analyzer()
            annotated_pdf_path = os.path.join(self.annotated_pdf_folder_path,os.path.basename(pdf_path))
            pdf_text = self._convert_pdf_to_text_ocr_with_layout_detection(analyzer,pdf_path,annotated_pdf_path)
        else:
            # Use plain Tesseract
            pdf_text = ''
            pdf_images = self._get_images_from_pdf(pdf_path)
            for image in pdf_images:
                text = self._extract_text_from_image(image,lang=lang)
                pdf_text += text
        return pdf_text

    def _convert_pdf_to_text_hybrid_and_write(self,file_path) -> str:
        # First check if the pdf is image based or text based
        doc_text = self._extract_text_without_ocr(file_path)
        if doc_text == '':
            # pdf is image based, use OCR
            doc_text = self._convert_pdf_to_text_ocr(file_path)
        output_text_file_path = os.path.join(self.output_text_folder_path, os.path.basename(file_path).replace('.pdf', '.txt'))
        with open(output_text_file_path, 'w') as f:
            f.write(doc_text)

    def perform_ocr(self):
        Parallel(n_jobs=-1)(
            delayed(self._convert_pdf_to_text_hybrid_and_write)(path) for path in
            tqdm(glob.glob(self.input_pdfs_folder + '/*.pdf')))



if __name__ == '__main__':
    experiment_name = '_plain_ocr'
    input_pdfs_folder = '/Users/prathamesh/tw_projects/OpenNyAI/data/LLM/Contracts for Review'
    output_text_folder_path = os.path.join(input_pdfs_folder,'output','text'+experiment_name)

    ocr = OCR(input_pdfs_folder,output_text_folder_path)
    ocr.perform_ocr()



