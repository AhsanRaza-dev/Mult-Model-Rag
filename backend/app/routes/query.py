"""
Query endpoints for text and image-based queries.
"""
import sys
from pathlib import Path

# Add RAG directory to path
rag_path = Path(__file__).parent.parent.parent.parent / "RAG"
sys.path.insert(0, str(rag_path))

from fastapi import APIRouter, HTTPException
from app.models import TextQueryRequest, QueryResponse, ErrorResponse
from query import QuerySystem

router = APIRouter()

# Initialize query system once (singleton pattern)
try:
    query_system = QuerySystem()
    print("✅ Query system initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize query system: {e}")
    query_system = None

@router.post("/text", response_model=QueryResponse, responses={500: {"model": ErrorResponse}})
async def query_text(request: TextQueryRequest):
    """
    Query the RAG system with a text question.
    
    Args:
        request: TextQueryRequest with query and top_k
        
    Returns:
        QueryResponse with answer and citations
        
    Raises:
        HTTPException: If query fails
    """
    if query_system is None:
        raise HTTPException(
            status_code=503,
            detail="Query system not initialized. Check server logs."
        )
    
    try:
        # Query the system
        result = query_system.query(
            text=request.query,
            top_k=request.top_k
        )
        
        # Check if query was successful
        if not result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Unknown error occurred")
            )
        
        # Return response
        return QueryResponse(
            success=result["success"],
            answer=result["answer"],
            citations=[
                {
                    "page": c["page"],
                    "file": c["file"],
                    "score": c["score"]
                }
                for c in result.get("citations", [])
            ],
            context_used=result.get("context_used", 0),
            search_query=result.get("search_query")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query failed: {str(e)}"
        )
