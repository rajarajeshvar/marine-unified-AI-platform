import os
from langchain_community.document_loaders import PyMuPDFLoader

pdf_path = os.path.join("dataset", "manuals", "0057319.pdf")
print(f"Loading {pdf_path}")
loader = PyMuPDFLoader(pdf_path)
pages = loader.load()

targets = ["110", "110 ± 5", "connecting-rod", "connecting rod"]

for i, page in enumerate(pages):
    text = page.page_content.replace('\n', ' ')
    if "110" in text and "connecting" in text.lower():
        print(f"Found on Page {i}: {text[:1000]}")
