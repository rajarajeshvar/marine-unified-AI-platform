import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))
DATASET_DIR = os.path.join(PROJECT_ROOT, 'dataset')
CHROMA_DB_DIR = os.path.join(BASE_DIR, 'chroma_db')

# --- LLM ---
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'ollama')
LLM_MODEL = os.getenv('LLM_MODEL', 'llama3.1')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')

# --- Embedding ---
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'BAAI/bge-small-en-v1.5')

# --- ChromaDB ---
CHROMA_COLLECTION_NAME = os.getenv('CHROMA_COLLECTION_NAME', 'marine_knowledge')

# --- Retrieval ---
RETRIEVAL_TOP_K = int(os.getenv('RETRIEVAL_TOP_K', '5'))
SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', '0.4'))

# --- Chunking ---
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '1000'))
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '150'))

# --- API ---
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '8005'))

# --- Memory ---
MAX_CONVERSATION_TURNS = int(os.getenv('MAX_CONVERSATION_TURNS', '10'))

# --- Data paths ---
SENSOR_DATA_CSV = os.path.join(DATASET_DIR, 'sensor data', 'marine_engine_sensor_data_120000.csv')
MAINTENANCE_LOG_CSV = os.path.join(DATASET_DIR, 'maintenance log', 'marine_maintenance_logs_6000.csv')
FAULT_DISTRIBUTION_CSV = os.path.join(DATASET_DIR, 'sensor data', 'fault_distribution.csv')
ENGINE_DATA_CSV = os.path.join(DATASET_DIR, 'manuals', 'marine_engine_data.csv')
ENGINE_FAULT_CSV = os.path.join(DATASET_DIR, 'manuals', 'marine_engine_fault_dataset.csv')
