"""
Marine Guardian AI — Document Ingestion Pipeline

Ingests PDFs (SOPs, Manuals) and maintenance logs (CSV) into ChromaDB
with rich metadata for filtered retrieval.

Usage:
    python ingest.py           # Incremental ingest (skips if collection exists)
    python ingest.py --reset   # Wipe collection and re-ingest everything
"""

import os
import re
import sys
import csv
import glob
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

from config import (
    DATASET_DIR, CHROMA_DB_DIR, EMBEDDING_MODEL,
    CHROMA_COLLECTION_NAME, CHUNK_SIZE, CHUNK_OVERLAP,
    MAINTENANCE_LOG_CSV,
)


def clean_text(text: str) -> str:
    """Remove junk characters and normalize whitespace from extracted PDF text."""
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)  # control chars
    text = re.sub(r'\n{3,}', '\n\n', text)                       # excessive newlines
    text = re.sub(r' {2,}', ' ', text)                           # excessive spaces
    return text.strip()


def classify_document(filepath: str) -> dict:
    """Derive metadata tags from the file path and name."""
    basename = os.path.basename(filepath)
    name_lower = basename.lower()

    meta = {"source_file": basename}

    if 'SOP' in filepath:
        meta["document_type"] = "SOP"
        meta["source_type"] = "standard_operating_procedure"
        # Extract equipment hint from filename
        equip = basename.replace('_SOP.pdf', '').replace('_', ' ')
        meta["equipment_hint"] = equip
    elif 'manuals' in filepath:
        meta["document_type"] = "manual"
        meta["source_type"] = "maintenance_manual"
        equip = basename.replace('_Manual.pdf', '').replace('.pdf', '').replace('_', ' ')
        meta["equipment_hint"] = equip
    else:
        meta["document_type"] = "document"
        meta["source_type"] = "general"
        meta["equipment_hint"] = ""

    return meta


def load_pdfs() -> list[Document]:
    """Load ALL PDFs from SOPs and Manuals directories."""
    docs = []

    # --- SOPs ---
    sop_dir = os.path.join(DATASET_DIR, 'SOP')
    print(f"\n📋 Loading SOPs from {sop_dir}...")
    for filepath in sorted(glob.glob(os.path.join(sop_dir, '*.pdf'))):
        try:
            loader = PyMuPDFLoader(filepath)
            pages = loader.load()
            custom_meta = classify_document(filepath)
            for page in pages:
                page.page_content = clean_text(page.page_content)
                page.metadata.update(custom_meta)
            docs.extend(pages)
            print(f"  ✓ {os.path.basename(filepath)} ({len(pages)} pages)")
        except Exception as e:
            print(f"  ✗ {os.path.basename(filepath)}: {e}")

    # --- Manuals (ALL PDFs, not just *Manual.pdf) ---
    manuals_dir = os.path.join(DATASET_DIR, 'manuals')
    print(f"\n📘 Loading Manuals from {manuals_dir}...")
    for filepath in sorted(glob.glob(os.path.join(manuals_dir, '*.pdf'))):
        try:
            loader = PyMuPDFLoader(filepath)
            pages = loader.load()
            custom_meta = classify_document(filepath)
            for page in pages:
                page.page_content = clean_text(page.page_content)
                page.metadata.update(custom_meta)
            docs.extend(pages)
            print(f"  ✓ {os.path.basename(filepath)} ({len(pages)} pages)")
        except Exception as e:
            print(f"  ✗ {os.path.basename(filepath)}: {e}")

    return docs


def load_maintenance_logs() -> list[Document]:
    """Load maintenance log CSV rows as documents with rich metadata."""
    docs = []
    if not os.path.exists(MAINTENANCE_LOG_CSV):
        print(f"\n⚠ Maintenance log not found at {MAINTENANCE_LOG_CSV}")
        return docs

    print(f"\n🛠 Loading Maintenance Logs from {MAINTENANCE_LOG_CSV}...")
    with open(MAINTENANCE_LOG_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            # Build a natural-language text representation of the log entry
            text = (
                f"Maintenance Record — {row.get('Date', 'Unknown Date')}\n"
                f"Equipment: {row.get('Equipment', 'N/A')} ({row.get('Equipment Type', 'N/A')})\n"
                f"Fault: {row.get('Fault', 'N/A')}\n"
                f"Fault Code: {row.get('Fault Code', 'N/A')}\n"
                f"Severity: {row.get('Severity', 'N/A')}\n"
                f"Action Taken: {row.get('Action Taken', 'N/A')}\n"
                f"Maintenance Type: {row.get('Maintenance Type', 'N/A')}\n"
                f"Engineer: {row.get('Engineer', 'N/A')}\n"
                f"Running Hours: {row.get('Running Hours', 'N/A')}\n"
                f"Downtime Hours: {row.get('Downtime Hours', 'N/A')}\n"
                f"Cost (USD): {row.get('Cost USD', 'N/A')}\n"
                f"Status: {row.get('Status', 'N/A')}\n"
                f"Remarks: {row.get('Remarks', 'N/A')}\n"
                f"Sensor Reading: {row.get('Sensor Reading', 'N/A')} {row.get('Sensor Unit', '')}\n"
                f"Recommended Action: {row.get('Recommended Action', 'N/A')}\n"
                f"Next Inspection: {row.get('Next Inspection Hours', 'N/A')} hours"
            )

            metadata = {
                "document_type": "maintenance_log",
                "source_type": "maintenance_record",
                "source_file": "marine_maintenance_logs_6000.csv",
                "equipment": row.get('Equipment', ''),
                "equipment_type": row.get('Equipment Type', ''),
                "equipment_hint": row.get('Equipment', ''),
                "severity": row.get('Severity', ''),
                "fault_code": row.get('Fault Code', ''),
                "maintenance_type": row.get('Maintenance Type', ''),
                "date": row.get('Date', ''),
            }
            docs.append(Document(page_content=text, metadata=metadata))

    print(f"  ✓ Loaded {len(docs)} maintenance log entries")
    return docs


def main():
    reset = '--reset' in sys.argv

    if reset:
        import shutil
        if os.path.exists(CHROMA_DB_DIR):
            print(f"🗑  Resetting ChromaDB at {CHROMA_DB_DIR}...")
            shutil.rmtree(CHROMA_DB_DIR)
            print("  ✓ Cleared.")

    # Load all documents
    pdf_docs = load_pdfs()
    log_docs = load_maintenance_logs()
    all_docs = pdf_docs + log_docs

    if not all_docs:
        print("\n❌ No documents found. Check your dataset directory.")
        return

    print(f"\n📊 Total documents loaded: {len(all_docs)}")

    # Chunk
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    splits = text_splitter.split_documents(all_docs)
    print(f"📦 Split into {len(splits)} chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")

    # Embed and store
    print(f"\n🧠 Generating embeddings with {EMBEDDING_MODEL}...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=CHROMA_DB_DIR,
        collection_name=CHROMA_COLLECTION_NAME,
    )
    vectorstore.persist()

    print(f"\n✅ Vectorstore persisted at {CHROMA_DB_DIR}")
    print(f"   Collection: {CHROMA_COLLECTION_NAME}")
    print(f"   Total chunks: {vectorstore._collection.count()}")


if __name__ == "__main__":
    main()
