# Backend API Testing Guide

## Server Status

✅ **Server Running**: http://localhost:8000
✅ **API Docs**: http://localhost:8000/docs (Swagger UI)
✅ **ReDoc**: http://localhost:8000/redoc

## Endpoints

### 1. Root Endpoint
```bash
GET /
```

**Response:**
```json
{
  "name": "FixIt.AI API",
  "version": "1.0.0",
  "description": "Machinery repair assistant with RAG",
  "docs": "/docs",
  "health": "/health",
  "stats": "/stats"
}
```

### 2. Health Check
```bash
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "documents": 913
}
```

### 3. Collection Statistics
```bash
GET /stats
```

**Response:**
```json
{
  "total_vectors": 913,
  "vector_dimension": 384,
  "distance_metric": "Cosine"
}
```

### 4. Text Query
```bash
POST /query/text
Content-Type: application/json

{
  "query": "How do I replace the brake pads?",
  "top_k": 3
}
```

**Response:**
```json
{
  "success": true,
  "answer": "To replace the brake pads, follow the procedures...",
  "citations": [
    {
      "page": "564",
      "file": "62sh300.pdf",
      "score": 0.818
    },
    {
      "page": "535",
      "file": "62sh300.pdf",
      "score": 0.817
    },
    {
      "page": "562",
      "file": "62sh300.pdf",
      "score": 0.809
    }
  ],
  "context_used": 3,
  "search_query": "How do I replace the brake pads?"
}
```

## Testing with PowerShell

### Health Check
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
```

### Stats
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/stats" -Method GET
```

### Text Query
```powershell
$body = @{
    query = "How do I replace the brake pads?"
    top_k = 3
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/query/text" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

## Testing with cURL

### Health Check
```bash
curl http://localhost:8000/health
```

### Stats
```bash
curl http://localhost:8000/stats
```

### Text Query
```bash
curl -X POST http://localhost:8000/query/text \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I replace the brake pads?", "top_k": 3}'
```

## Testing with Python

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Stats
response = requests.get("http://localhost:8000/stats")
print(response.json())

# Text query
response = requests.post(
    "http://localhost:8000/query/text",
    json={
        "query": "How do I replace the brake pads?",
        "top_k": 3
    }
)
print(response.json())
```

## Running the Server

### Development Mode (with auto-reload)
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
  - Interactive API testing
  - Try out endpoints directly in browser
  
- **ReDoc**: http://localhost:8000/redoc
  - Clean, readable documentation
  - Better for sharing with team

## CORS Configuration

Currently configured to allow all origins (`*`) for development.

For production, update `backend/app/main.py`:
```python
allow_origins=[
    "http://localhost:3000",  # React dev server
    "https://yourdomain.com"   # Production domain
]
```

## Error Handling

The API returns proper HTTP status codes:

- `200 OK`: Successful request
- `422 Unprocessable Entity`: Validation error (invalid request body)
- `500 Internal Server Error`: Query processing error
- `503 Service Unavailable`: System not initialized

Example error response:
```json
{
  "success": false,
  "error": "Query failed: Connection timeout"
}
```
