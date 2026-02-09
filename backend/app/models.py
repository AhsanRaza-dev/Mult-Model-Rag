"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import List, Optional

class TextQueryRequest(BaseModel):
    """Request model for text-based queries."""
    query: str = Field(..., min_length=1, max_length=500, description="User's question")
    top_k: int = Field(default=5, ge=1, le=10, description="Number of context chunks to retrieve")

class Citation(BaseModel):
    """Citation information for a source."""
    page: str = Field(..., description="Page number")
    file: str = Field(..., description="Source file name")
    score: float = Field(..., description="Relevance score (0-1)")

class QueryResponse(BaseModel):
    """Response model for query results."""
    success: bool = Field(..., description="Whether query was successful")
    answer: str = Field(..., description="Generated answer")
    citations: List[Citation] = Field(..., description="Source citations")
    context_used: int = Field(..., description="Number of context chunks used")
    search_query: Optional[str] = Field(None, description="Enhanced search query (if applicable)")

class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = Field(default=False)
    error: str = Field(..., description="Error message")

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    documents: int = Field(..., description="Number of indexed documents")

class StatsResponse(BaseModel):
    """Collection statistics response."""
    total_vectors: int = Field(..., description="Total number of vectors")
    vector_dimension: int = Field(..., description="Vector dimensionality")
    distance_metric: str = Field(..., description="Distance metric used")
