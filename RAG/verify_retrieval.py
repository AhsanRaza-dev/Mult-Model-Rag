import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import qdrant_client

# Load environment variables
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if not QDRANT_URL:
    raise ValueError("QDRANT_URL not found in .env file")
if not QDRANT_API_KEY:
    raise ValueError("QDRANT_API_KEY not found in .env file")

def verify_retrieval(query_text="How do I fix the extruder?"):
    print("Initializing Local Embedding Model...")
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

    # Check collection info
    collection_info = client.get_collection(collection_name="fixit_manuals")
    print(f"\n=== Collection Info ===")
    print(f"Total vectors: {collection_info.points_count}")
    print(f"Vector dimension: {collection_info.config.params.vectors.size}")
    print(f"Distance metric: {collection_info.config.params.vectors.distance}")
    print()

    vector_store = QdrantVectorStore(client=client, collection_name="fixit_manuals")
    
    # Load index from vector store
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    print(f"Querying: '{query_text}'")
    retriever = index.as_retriever(similarity_top_k=3)
    nodes = retriever.retrieve(query_text)

    if not nodes:
        print("No nodes retrieved. Check if data was ingested.")
        return

    print(f"\nRetrieved {len(nodes)} nodes:\n")
    for i, node in enumerate(nodes):
        print(f"--- Node {i+1} (Score: {node.score:.4f}) ---")
        print(f"Metadata: {node.metadata}")
        print(f"Content (first 500 chars):\n{node.text[:500]}\n")
        print(f"Full content length: {len(node.text)} characters\n")

if __name__ == "__main__":
    verify_retrieval()
