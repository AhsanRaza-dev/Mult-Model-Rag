"""
RAG pipeline for retrieval and context formatting.
"""
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
import qdrant_client

class RAGPipeline:
    """RAG pipeline for retrieving and formatting context."""
    
    def __init__(self):
        """Initialize RAG pipeline with Qdrant connection."""
        load_dotenv()
        
        # Initialize embedding model (same as ingestion)
        self.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )
        Settings.embed_model = self.embed_model
        Settings.llm = None
        
        # Connect to Qdrant
        self.client = qdrant_client.QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
        )
        
        # Load index
        vector_store = QdrantVectorStore(
            client=self.client,
            collection_name="fixit_manuals"
        )
        self.index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve relevant context from vector database.
        
        Args:
            query: Search query
            top_k: Number of results to retrieve
            
        Returns:
            List of context dictionaries with text, metadata, and scores
        """
        try:
            # Create retriever
            retriever = self.index.as_retriever(similarity_top_k=top_k)
            
            # Retrieve nodes
            nodes = retriever.retrieve(query)
            
            # Format results
            results = []
            for node in nodes:
                results.append({
                    'text': node.text,
                    'metadata': node.metadata,
                    'score': node.score
                })
            
            return results
            
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return []
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the vector collection."""
        try:
            collection_info = self.client.get_collection(collection_name="fixit_manuals")
            return {
                'total_vectors': collection_info.points_count,
                'vector_dimension': collection_info.config.params.vectors.size,
                'distance_metric': collection_info.config.params.vectors.distance
            }
        except Exception as e:
            return {'error': str(e)}
