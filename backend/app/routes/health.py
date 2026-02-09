"""
Health check and statistics endpoints.
"""
import sys
from pathlib import Path

# Add RAG directory to path
rag_path = Path(__file__).parent.parent.parent.parent / "RAG"
sys.path.insert(0, str(rag_path))

from fastapi import APIRouter, HTTPException
from app.models import HealthResponse, StatsResponse
from rag_pipeline import RAGPipeline

router = APIRouter()

# Initialize RAG pipeline once
try:
    rag = RAGPipeline()
    print("✅ RAG pipeline initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize RAG pipeline: {e}")
    rag = None

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        HealthResponse with status and document count
    """
    if rag is None:
        raise HTTPException(
            status_code=503,
            detail="RAG pipeline not initialized"
        )
    
    try:
        stats = rag.get_collection_stats()
        return HealthResponse(
            status="ok",
            documents=stats.get("total_vectors", 0)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )

@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get collection statistics.
    
    Returns:
        StatsResponse with vector count, dimensions, and metric
    """
    if rag is None:
        raise HTTPException(
            status_code=503,
            detail="RAG pipeline not initialized"
        )
    
    try:
        stats = rag.get_collection_stats()
        
        if "error" in stats:
            raise HTTPException(
                status_code=500,
                detail=stats["error"]
            )
        
        return StatsResponse(
            total_vectors=stats.get("total_vectors", 0),
            vector_dimension=stats.get("vector_dimension", 0),
            distance_metric=stats.get("distance_metric", "Unknown")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get stats: {str(e)}"
        )
