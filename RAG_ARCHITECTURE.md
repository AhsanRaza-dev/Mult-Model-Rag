# FixIt.AI RAG System - Complete Architecture & Components

## Overview

This document explains the complete RAG (Retrieval-Augmented Generation) system architecture, components, and data flow.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERACTION                          │
│                                                              │
│  Web Browser → Streamlit (Port 8501) → FastAPI (Port 8000) │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    QUERY PROCESSING                          │
│                                                              │
│  1. Receive Query → 2. Generate Embedding → 3. Vector Search│
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    RAG PIPELINE                              │
│                                                              │
│  Qdrant DB → Retrieve Top-K → Format Context → Gemini LLM  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    RESPONSE GENERATION                       │
│                                                              │
│  Answer + Citations → JSON Response → Display to User       │
└─────────────────────────────────────────────────────────────┘
```

## Phase 1: Data Ingestion (One-Time Setup)

### Step 1: PDF Loading with OCR

**File:** `RAG/ocr_pdf_reader.py`

**Purpose:** Extract text from scanned PDF manuals

**Technology:**
- **PyMuPDF (fitz)**: PDF page rendering
- **Tesseract OCR**: Text extraction from images
- **Pillow**: Image processing

**Process:**
1. Load PDF file
2. Check each page for text
3. If no text found → Convert page to image
4. Apply OCR to extract text
5. Return text content

**Code Flow:**
```python
PDF → PyMuPDF → Check Text
                    ↓ (if empty)
                Image Conversion (2x zoom)
                    ↓
                Tesseract OCR
                    ↓
                Extracted Text
```

### Step 2: Text Chunking

**File:** `RAG/ingestion.py`

**Purpose:** Split documents into manageable chunks

**Technology:**
- **LlamaIndex**: Document processing framework

**Process:**
1. Load documents with OCR
2. Split into chunks (default: ~512 tokens)
3. Create nodes with metadata (page numbers, file names)

**Result:** 913 document chunks from 899 pages

### Step 3: Embedding Generation

**File:** `RAG/ingestion.py`

**Purpose:** Convert text to numerical vectors

**Technology:**
- **Model**: BAAI/bge-small-en-v1.5
- **Framework**: sentence-transformers
- **Dimensions**: 384

**Process:**
1. Load local embedding model
2. Process each chunk
3. Generate 384-dimensional vector
4. Store embeddings

**Performance:** 4.25 embeddings/second

### Step 4: Vector Storage

**File:** `RAG/ingestion.py`

**Purpose:** Store embeddings for fast retrieval

**Technology:**
- **Qdrant Cloud**: Vector database
- **Distance Metric**: Cosine similarity

**Process:**
1. Connect to Qdrant
2. Create collection "fixit_manuals"
3. Upload vectors with metadata
4. Index for fast search

**Result:** 913 vectors stored

## Phase 2: Query Processing (Runtime)

### Step 1: Query Reception

**File:** `backend/app/routes/query.py`

**Purpose:** Receive user query via API

**Technology:**
- **FastAPI**: Web framework
- **Pydantic**: Request validation

**Process:**
1. Receive POST request
2. Validate query (1-500 chars)
3. Validate top_k (1-10)
4. Pass to query system

### Step 2: Query Embedding

**File:** `RAG/query.py`

**Purpose:** Convert query to vector

**Technology:**
- **Same model**: BAAI/bge-small-en-v1.5

**Process:**
1. Load query text
2. Generate embedding (384 dims)
3. Prepare for vector search

### Step 3: Vector Retrieval

**File:** `RAG/rag_pipeline.py`

**Purpose:** Find similar documents

**Technology:**
- **Qdrant Client**: Vector search
- **Cosine Similarity**: Distance metric

**Process:**
1. Query Qdrant with embedding
2. Retrieve top-k similar vectors
3. Get metadata (page, file, score)
4. Format as context

**Example Results:**
- Page 564: Score 0.818
- Page 535: Score 0.817
- Page 562: Score 0.809

### Step 4: Context Formatting

**File:** `RAG/rag_pipeline.py`

**Purpose:** Prepare context for LLM

**Process:**
1. Extract text from retrieved chunks
2. Add page numbers
3. Format as structured context
4. Limit to top-k results

### Step 5: Answer Generation

**File:** `RAG/gemini_client.py`

**Purpose:** Generate answer using LLM

**Technology:**
- **Model**: gemini-3-flash-preview
- **Package**: google-genai
- **API**: Google AI Studio

**Process:**
1. Create prompt with context
2. Include user query
3. Send to Gemini API
4. Receive generated answer
5. Extract citations

**Prompt Structure:**
```
Context: [Retrieved chunks with page numbers]
Question: [User query]
Instructions: Answer based on context, cite sources
```

### Step 6: Response Formatting

**File:** `backend/app/routes/query.py`

**Purpose:** Format response as JSON

**Response Structure:**
```json
{
  "success": true,
  "answer": "Detailed answer...",
  "citations": [
    {"page": "564", "file": "62sh300.pdf", "score": 0.818}
  ],
  "context_used": 3
}
```

## Phase 3: Frontend Display

### Step 1: User Interface

**File:** `frontend/app.py`

**Purpose:** Web interface for queries

**Technology:**
- **Streamlit**: Python web framework

**Components:**
1. **Query Input**: Text area
2. **Submit Button**: Trigger query
3. **Stats Sidebar**: System info
4. **Answer Display**: Formatted response
5. **Citations Panel**: Source references
6. **Query History**: Previous queries

### Step 2: API Communication

**Process:**
1. User enters query
2. Frontend sends POST to backend
3. Wait for response (60s timeout)
4. Display results

## Technologies Used

### Data Processing
| Component | Technology | Purpose |
|-----------|-----------|---------|
| PDF Reading | PyMuPDF | Page rendering |
| OCR | Tesseract 4.0+ | Text extraction |
| Image Processing | Pillow | Image manipulation |
| Document Processing | LlamaIndex | Chunking & indexing |

### Embeddings
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Model | BAAI/bge-small-en-v1.5 | Text → Vector |
| Framework | sentence-transformers | Model loading |
| Compute | CPU (local) | Inference |
| Dimensions | 384 | Vector size |

### Vector Database
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Database | Qdrant Cloud | Vector storage |
| Metric | Cosine Similarity | Distance calculation |
| Client | qdrant-client | API communication |

### Language Model
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Model | gemini-3-flash-preview | Answer generation |
| API | google-genai | Communication |
| Provider | Google AI Studio | Hosting |
| Free Tier | 1500 req/day | Rate limit |

### Backend API
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | FastAPI | REST API |
| Server | Uvicorn | ASGI server |
| Validation | Pydantic | Request/response |
| CORS | FastAPI middleware | Cross-origin |

### Frontend
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | Streamlit | Web UI |
| HTTP Client | requests | API calls |
| Styling | Custom CSS | UI design |

## Data Flow Example

**User Query:** "How do I replace the brake pads?"

### Step-by-Step:

1. **User Input** (Streamlit)
   - User types query
   - Clicks "Ask Question"

2. **Frontend Processing** (frontend/app.py)
   - Validates input
   - Sends POST to `http://localhost:8000/query/text`
   - JSON: `{"query": "How do I replace the brake pads?", "top_k": 5}`

3. **Backend Reception** (backend/app/routes/query.py)
   - Receives request
   - Validates with Pydantic
   - Passes to QuerySystem

4. **Query Embedding** (RAG/query.py)
   - Loads BAAI/bge-small-en-v1.5
   - Generates 384-dim vector
   - Example: `[0.123, -0.456, 0.789, ...]`

5. **Vector Search** (RAG/rag_pipeline.py)
   - Queries Qdrant with vector
   - Searches 913 vectors
   - Finds top 5 similar chunks
   - Returns with scores

6. **Context Retrieval**
   - Chunk 1: Page 564 (Score: 0.818)
   - Chunk 2: Page 535 (Score: 0.817)
   - Chunk 3: Page 562 (Score: 0.809)
   - Chunk 4: Page 520 (Score: 0.795)
   - Chunk 5: Page 507 (Score: 0.778)

7. **Context Formatting**
   ```
   [Page 564] Remove caliper bolts (8 x 1.0 mm)...
   [Page 535] Brake pad replacement procedure...
   [Page 562] Torque specifications: 23 N·m...
   ```

8. **LLM Generation** (RAG/gemini_client.py)
   - Sends context + query to Gemini
   - Receives generated answer
   - Extracts citations

9. **Response Formation**
   ```json
   {
     "success": true,
     "answer": "To replace brake pads: 1. Remove caliper...",
     "citations": [
       {"page": "564", "file": "62sh300.pdf", "score": 0.818}
     ],
     "context_used": 5
   }
   ```

10. **Frontend Display** (frontend/app.py)
    - Shows answer
    - Lists citations
    - Displays response time
    - Adds to history

## Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| **Ingestion** |
| OCR Time | ~4 hours | One-time, 899 pages |
| Embedding Time | 3m 34s | One-time, 913 chunks |
| **Query** |
| Embedding | < 1s | Per query |
| Vector Search | < 1s | Qdrant search |
| LLM Generation | 3-8s | Gemini API |
| Total Query Time | 5-10s | End-to-end |
| **Accuracy** |
| Retrieval Score | 0.74-0.82 | Top results |
| Answer Quality | High | With citations |

## File Structure

```
RAG/
├── ocr_pdf_reader.py      # OCR implementation
├── ingestion.py           # Data ingestion pipeline
├── rag_pipeline.py        # Vector retrieval
├── gemini_client.py       # LLM wrapper
├── query.py               # Query orchestration
└── data/pdfs/             # Source PDFs

backend/
├── app/
│   ├── main.py           # FastAPI app
│   ├── models.py         # Pydantic schemas
│   └── routes/
│       ├── query.py      # Query endpoint
│       └── health.py     # Health endpoints

frontend/
└── app.py                # Streamlit UI
```

## Environment Variables

```env
GEMINI_API_KEY=your_gemini_key      # Google AI Studio
QDRANT_URL=your_qdrant_url          # Qdrant Cloud
QDRANT_API_KEY=your_qdrant_key      # Qdrant API key
```

## Key Design Decisions

1. **Local Embeddings**: 150x faster than API, no rate limits
2. **Qdrant Cloud**: Managed service, no local setup
3. **Gemini Flash**: Fast, free tier sufficient
4. **Streamlit**: Rapid UI development
5. **FastAPI**: Auto-generated docs, type safety
6. **OCR**: Essential for scanned PDFs

## Summary

The RAG system combines:
- **OCR** for scanned PDFs
- **Local embeddings** for speed
- **Vector search** for retrieval
- **Gemini LLM** for generation
- **FastAPI** for backend
- **Streamlit** for frontend

All working together to provide accurate, cited answers to machinery repair questions.
