import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import qdrant_client
from ocr_pdf_reader import OCRPDFReader
from pathlib import Path

# Load environment variables
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if not QDRANT_URL:
    raise ValueError("QDRANT_URL not found in .env file")
if not QDRANT_API_KEY:
    raise ValueError("QDRANT_API_KEY not found in .env file")

def ingest_data():
    print("Initializing Local Embedding Model...")
    # Using BAAI/bge-small-en-v1.5 locally (384 dimensions)
    # Fast and runs on CPU
    embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )
    Settings.embed_model = embed_model
    Settings.llm = None 

    print("Connecting to Qdrant...")
    client = qdrant_client.QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
    )

    # Re-create collection to ensure correct dimension (384 for bge-small-en-v1.5)
    collection_name = "fixit_manuals"
    print(f"Ensuring collection '{collection_name}' exists with dimension 384...")
    try:
        client.delete_collection(collection_name=collection_name)
        print("Deleted existing collection to reset dimensions.")
    except Exception:
        pass # Collection might not exist

    # Vector store will create collection if missing
    vector_store = QdrantVectorStore(client=client, collection_name=collection_name)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    print("Loading PDFs with OCR from data/pdfs...")
    try:
        # Use OCR-enabled PDF reader
        reader = OCRPDFReader(use_ocr=True)
        pdf_path = Path("./data/pdfs/62sh300.pdf")
        
        documents = reader.load_data(pdf_path)
        print(f"Loaded {len(documents)} document chunks with OCR.")
    except Exception as e:
        print(f"Error loading PDFs: {e}")
        return

    print("Indexing Documents with Local Embeddings...")
    print("This will be much faster than API embeddings!")
    # Using local embeddings - no rate limits, runs on CPU
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True
    )
    print("Ingestion Complete!")

if __name__ == "__main__":
    ingest_data()
