"""
FastAPI application for FixIt.AI machinery repair assistant.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import query, health

# Create FastAPI app
app = FastAPI(
    title="FixIt.AI API",
    description="Machinery repair assistant with RAG (Retrieval-Augmented Generation)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production: ["http://localhost:3000", "https://yourdomain.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(query.router, prefix="/query", tags=["Query"])

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "FixIt.AI API",
        "version": "1.0.0",
        "description": "Machinery repair assistant with RAG",
        "docs": "/docs",
        "health": "/health",
        "stats": "/stats"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
