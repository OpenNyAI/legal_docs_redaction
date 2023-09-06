from docx.text.paragraph import Paragraph
from docx.document import Document
from docx.table import _Cell, Table
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
import docx
from operator import itemgetter
import pdfplumber
import re
def iter_docx_block_items(parent):
    if isinstance(parent, Document):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        raise ValueError("something's not right")

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)
            # for row in table.rows:
            #     for cell in row.cells:
            #         yield from iter_block_items(cell)
def parse_docx(file_name) -> list[str|Table]:
    # Parse a docx file into a list of (paragraph_text, table) elements.
    doc = docx.Document(file_name)
    doc_elements = []
    doc_text = ''
    for block in iter_docx_block_items(doc):
        if isinstance(block, Paragraph):
            doc_text = doc_text + '\n' + block.text

        elif isinstance(block, Table):
            doc_elements.append(doc_text)
            doc_elements.append(block)
            doc_text = ''
    if doc_text != '':
        doc_elements.append(doc_text)
    return doc_elements

def check_bboxes(word, table_bbox):
    """
    Check whether word is inside a table bbox.
    """
    l = word['x0'], word['top'], word['x1'], word['bottom']
    r = table_bbox
    return l[0] > r[0] and l[1] > r[1] and l[2] < r[2] and l[3] < r[3]
def parse_pdf(pdf_file_path) ->list:
    parsed_pdf = []
    with pdfplumber.open(pdf_file_path) as pdf:
        for page in pdf.pages:
            tables = page.find_tables()
            table_bboxes = [i.bbox for i in tables]
            tables = [{'table': i.extract(), 'top': i.bbox[1]} for i in tables]
            non_table_words = [word for word in page.extract_words() if not any(
                [check_bboxes(word, table_bbox) for table_bbox in table_bboxes])]
            for cluster in pdfplumber.utils.cluster_objects(
                    non_table_words + tables, itemgetter('top'), tolerance=5):
                if 'text' in cluster[0]:
                    parsed_pdf.append(' '.join([i['text'] for i in cluster]))
                elif 'table' in cluster[0]:
                    parsed_pdf.append(cluster[0]['table'])
    return parsed_pdf

def sanitize_str(s):
    control_chars = "\x00-\x1f\x7f-\x9f"
    control_char_re = re.compile("[%s]" % control_chars)
    return control_char_re.sub("", s)

if __name__ == "__main__":
    parse_pdf('/Users/prathamesh/tw_projects/OpenNyAI/data/LLM/Legal Documents - Atreyo/test1.pdf')
    #parse_pdf('/Users/prathamesh/tw_projects/OpenNyAI/data/LLM/Contracts for Review/GTC - Lipika.pdf')