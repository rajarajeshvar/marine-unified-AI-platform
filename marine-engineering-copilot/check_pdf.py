import os
from langchain_community.document_loaders import PyMuPDFLoader

pdf_path = os.path.join("dataset", "manuals", "0057319.pdf")
print(f"Loading {pdf_path}")
try:
    loader = PyMuPDFLoader(pdf_path)
    pages = loader.load()
    if len(pages) >= 234:
        # Langchain pages are 0-indexed, but does user mean physical page 234 (index 233) or 235 (index 234)?
        print("--- PAGE 233 ---")
        print(pages[233].page_content)
        print("--- PAGE 234 ---")
        print(pages[234].page_content)
        print("--- PAGE 235 ---")
        print(pages[235].page_content)
    else:
        print(f"Only {len(pages)} pages found.")
except Exception as e:
    print(f"Error: {e}")
