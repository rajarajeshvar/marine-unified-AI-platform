import os
import sys
from langchain_community.document_loaders import PyMuPDFLoader

sys.stdout.reconfigure(encoding='utf-8')

def check_page(pdf_name, page_index):
    pdf_path = os.path.join("dataset", "manuals", pdf_name)
    if not os.path.exists(pdf_path):
        pdf_path = os.path.join("dataset", "SOP", pdf_name)
    loader = PyMuPDFLoader(pdf_path)
    pages = loader.load()
    if page_index < len(pages):
        text = pages[page_index].page_content.replace('\n', ' ')
        print(f"[{pdf_name}] Page {page_index}: {text[:500]}...")
    else:
        print(f"[{pdf_name}] doesn't have page {page_index}")

check_page("0057319.pdf", 380)
check_page("0057319.pdf", 374)
check_page("a043m526-i13-hdkcx-service-manual.pdf", 82)
check_page("0057095.pdf", 9)
