"""
Main query interface for the RAG system.
Supports text queries and image-based queries.
"""
import os
from typing import Optional, Dict
from dotenv import load_dotenv
from gemini_client import GeminiClient
from rag_pipeline import RAGPipeline

# Load environment variables
load_dotenv()

class QuerySystem:
    """Main query system combining vision, retrieval, and generation."""
    
    def __init__(self):
        """Initialize query system components."""
        # GeminiClient will read from GEMINI_API_KEY environment variable
        self.gemini = GeminiClient()
        self.rag = RAGPipeline()
        
        print("Query system initialized successfully!")
        stats = self.rag.get_collection_stats()
        print(f"Vector DB: {stats.get('total_vectors', 0)} documents indexed")
    
    def query(
        self,
        text: Optional[str] = None,
        image_path: Optional[str] = None,
        top_k: int = 5
    ) -> Dict:
        """
        Query the system with text and/or image.
        
        Args:
            text: Text query
            image_path: Path to image file
            top_k: Number of context chunks to retrieve
            
        Returns:
            Dictionary with answer, citations, and metadata
        """
        import time
        
        if not text and not image_path:
            return {
                "success": False,
                "error": "Please provide either a text query or an image"
            }
        
        image_analysis = None
        search_query = text
        
        # Step 1: Analyze image if provided
        if image_path:
            print(f"\nAnalyzing image: {image_path}")
            analysis_result = self.gemini.analyze_image(image_path)
            
            if not analysis_result["success"]:
                return {
                    "success": False,
                    "error": f"Image analysis failed: {analysis_result.get('error')}"
                }
            
            image_analysis = analysis_result["analysis"]
            print(f"Image analysis complete")
            
            # Enhance query based on image
            search_query = self.gemini.enhance_query(image_analysis, text)
            print(f"Enhanced query: {search_query}")
        
        # Step 2: Retrieve relevant context
        print(f"\n[TIMING] Starting retrieval...")
        start = time.time()
        print(f"Searching knowledge base...")
        context = self.rag.retrieve(search_query, top_k=top_k)
        retrieval_time = time.time() - start
        print(f"[TIMING] Retrieval took {retrieval_time:.2f}s")
        
        if not context:
            return {
                "success": False,
                "error": "No relevant information found in the manual"
            }
        
        print(f"Retrieved {len(context)} relevant sections")
        
        # Step 3: Generate answer
        print(f"\n[TIMING] Starting answer generation...")
        start = time.time()
        print(f"Generating answer...")
        result = self.gemini.generate_answer(
            query=text or search_query,
            context=context,
            image_analysis=image_analysis
        )
        generation_time = time.time() - start
        print(f"[TIMING] Answer generation took {generation_time:.2f}s")
        print(f"[TIMING] TOTAL TIME: {retrieval_time + generation_time:.2f}s")
        
        # Add search query to result
        result["search_query"] = search_query
        if image_analysis:
            result["image_analysis"] = image_analysis
        
        return result

def main():
    """Example usage of the query system."""
    import sys
    
    # Initialize system
    system = QuerySystem()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        # Image query
        if sys.argv[1].endswith(('.jpg', '.jpeg', '.png', '.webp')):
            image_path = sys.argv[1]
            text_query = sys.argv[2] if len(sys.argv) > 2 else None
            result = system.query(text=text_query, image_path=image_path)
        else:
            # Text query
            text_query = ' '.join(sys.argv[1:])
            result = system.query(text=text_query)
    else:
        # Interactive mode
        print("\n" + "="*60)
        print("FixIt.AI - Machinery Repair Assistant")
        print("="*60)
        
        text_query = input("\nEnter your question: ").strip()
        image_path = input("Image path (optional, press Enter to skip): ").strip()
        
        if not image_path:
            image_path = None
        
        result = system.query(text=text_query, image_path=image_path)
    
    # Display results
    print("\n" + "="*60)
    if result["success"]:
        print("ANSWER:")
        print("="*60)
        print(result["answer"])
        
        print("\n" + "="*60)
        print("CITATIONS:")
        print("="*60)
        for i, citation in enumerate(result.get("citations", []), 1):
            print(f"{i}. Page {citation['page']} (Relevance: {citation['score']:.2f})")
        
        if "image_analysis" in result:
            print("\n" + "="*60)
            print("IMAGE ANALYSIS:")
            print("="*60)
            print(result["image_analysis"])
    else:
        print("ERROR:")
        print("="*60)
        print(result.get("error", "Unknown error"))
    
    print("="*60)

if __name__ == "__main__":
    main()
