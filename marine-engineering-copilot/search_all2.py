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
            if "connecting-rod" in text.lower() or "connecting rod" in text.lower():
                if "torque" in text.lower() or "ft-lb" in text.lower() or "n·m" in text.lower() or "nm" in text.lower() or "n m" in text.lower():
                    print(f"[{os.path.basename(pdf_path)}] Page {i}: {text[:100]}...")
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
