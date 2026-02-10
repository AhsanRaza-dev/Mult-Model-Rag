"""
Query endpoints for text and image-based queries.
"""
import sys
from pathlib import Path

# Add RAG directory to path
rag_path = Path(__file__).parent.parent.parent.parent / "RAG"
sys.path.insert(0, str(rag_path))

from fastapi import APIRouter, HTTPException
from ..models import TextQueryRequest, QueryResponse, ErrorResponse
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
            status_code=500,
            detail=f"Query failed: {str(e)}"
        )

@router.post("/image", response_model=QueryResponse, responses={500: {"model": ErrorResponse}})
async def query_image(
    image: UploadFile = File(...),
    query: Optional[str] = Form(None),
    top_k: int = Form(5)
):
    """
    Query the RAG system with an image and optional text.
    
    Args:
        image: Image file (multipart/form-data)
        query: Optional text query
        top_k: Number of context chunks
        
    Returns:
        QueryResponse with analysis, answer, and citations
    """
    from fastapi import File, Form, UploadFile
    from typing import Optional
    import shutil
    import os
    import tempfile
    
    if query_system is None:
        raise HTTPException(
            status_code=503,
            detail="Query system not initialized. Check server logs."
        )
    
    # Create temp file for image
    try:
        suffix = Path(image.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(image.file, tmp)
            tmp_path = tmp.name
        
        try:
            # Query the system
            result = query_system.query(
                text=query,
                image_path=tmp_path,
                top_k=top_k
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
                search_query=result.get("search_query"),
                image_analysis=result.get("image_analysis")
            )
            
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Image query failed: {str(e)}"
        )
