import os
import sys
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

sys.stdout.reconfigure(encoding='utf-8')

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
CHROMA_DB_DIR = os.path.join(os.getcwd(), "backend", "chroma_db")
CHROMA_COLLECTION_NAME = "marine_knowledge"

print("Loading vectorstore...")
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
vectorstore = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embeddings, collection_name=CHROMA_COLLECTION_NAME)

queries = [
    "connecting-rod bolt torque",
    "connecting rod bolts torque specification",
    "110 ± 5 N·m",
    "Engine 2 connecting-rod bolts",
    "Section 14 connecting-rod"
]

for query in queries:
    print(f"\n--- QUERY: {query} ---")
    results = vectorstore.similarity_search_with_relevance_scores(query, k=3)
    for i, (doc, score) in enumerate(results):
        print(f"Result {i+1}:")
        print(f"Document: {doc.metadata.get('source_file')}")
        page = doc.metadata.get('page')
        print(f"Page: {page if page is not None else 'N/A'}")
        print(f"Section: {doc.metadata.get('document_type', 'N/A')} - {doc.metadata.get('equipment_hint', 'N/A')}")
        print(f"Score: {score}")
        print(f"Chunk text: {doc.page_content.replace(chr(10), ' ')[:200]}...")
