import os
import glob
from langchain_community.document_loaders import PyMuPDFLoader

pdf_files = glob.glob("dataset/manuals/*.pdf") + glob.glob("dataset/SOP/*.pdf")

for pdf_path in pdf_files:
    try:
        loader = PyMuPDFLoader(pdf_path)
        pages = loader.load()
        for i, page in enumerate(pages):
            text = page.page_content.replace('\n', ' ')
            if "110" in text and "connecting" in text.lower():
                print(f"[{pdf_path}] Page {i}: {text[:1000]}")
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
