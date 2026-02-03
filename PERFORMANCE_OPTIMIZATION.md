# Query Performance Analysis & Optimization

## Current Performance: 34.24 seconds ⚠️

This is slower than expected. Let's break down where time is spent and how to optimize.

## Time Breakdown

Typical query should take **5-10 seconds**. Your 34s suggests bottlenecks.

### Expected Time Distribution:
```
1. Query Embedding:        0.5-1s   (Local model)
2. Vector Search:          0.5-1s   (Qdrant query)
3. Context Formatting:     0.1-0.5s (Text processing)
4. LLM Generation:         3-8s     (Gemini API)
5. Response Formatting:    0.1-0.5s (JSON creation)
-------------------------------------------
Total Expected:            5-11s
```

### Your Time: 34s
**Likely Bottlenecks:**
1. ❌ Model loading on each request (should be cached)
2. ❌ Slow network to Gemini API
3. ❌ Large context size (too many chunks)
4. ❌ Embedding model reloading

## Optimization Strategies

### 1. Cache Embedding Model ✅ (Already Done)

**Current Implementation:**
```python
# In rag_pipeline.py
class RAGPipeline:
    def __init__(self):
        self.embed_model = HuggingFaceEmbedding(...)  # Loaded once
```

**Status:** ✅ Model is cached in class instance

### 2. Reduce Context Size 🔧

**Current:** Retrieving 5 chunks (default)
**Recommendation:** Reduce to 3 chunks

**Why:** Less text to send to Gemini = faster response

**How to Fix:**

In `frontend/app.py`, change default:
```python
# Line 92
top_k = st.number_input("Results", min_value=1, max_value=10, value=3)  # Changed from 5
```

**Expected Improvement:** 5-10 seconds faster

### 3. Check Gemini API Latency 🔧

**Issue:** Gemini API might be slow from your location

**Test API Speed:**
```python
import time
import requests

start = time.time()
response = requests.post(
    "http://localhost:8000/query/text",
    json={"query": "test", "top_k": 1}
)
print(f"Time: {time.time() - start:.2f}s")
```

**If > 20s:** Gemini API is the bottleneck

**Solutions:**
- Use Gemini 1.5 Flash (might be faster)
- Consider local LLM (Ollama + Llama 3)
- Check internet connection

### 4. Optimize Embedding Generation 🔧

**Current:** CPU-based embedding
**Issue:** Might be slow on first query

**Check if model is reloading:**

Add logging to `RAG/rag_pipeline.py`:
```python
def retrieve(self, query: str, top_k: int = 5):
    print(f"[DEBUG] Starting retrieval at {time.time()}")
    
    # Generate query embedding
    print(f"[DEBUG] Generating embedding...")
    start = time.time()
    query_embedding = self.embed_model.get_query_embedding(query)
    print(f"[DEBUG] Embedding took {time.time() - start:.2f}s")
    
    # Search
    print(f"[DEBUG] Searching Qdrant...")
    start = time.time()
    results = self.index.as_retriever(similarity_top_k=top_k).retrieve(query)
    print(f"[DEBUG] Search took {time.time() - start:.2f}s")
```

### 5. Use Smaller Model for Embeddings 🔧

**Current:** BAAI/bge-small-en-v1.5 (384 dims)
**Alternative:** all-MiniLM-L6-v2 (384 dims, faster)

**Trade-off:** Slightly lower accuracy for 2x speed

### 6. Implement Caching 🔧

**Cache frequent queries:**

```python
# In backend/app/routes/query.py
from functools import lru_cache

query_cache = {}

@router.post("/text")
async def query_text(request: TextQueryRequest):
    # Check cache
    cache_key = f"{request.query}_{request.top_k}"
    if cache_key in query_cache:
        return query_cache[cache_key]
    
    # Process query
    result = query_system.query(...)
    
    # Cache result
    query_cache[cache_key] = result
    return result
```

**Expected Improvement:** Instant for repeated queries

### 7. Profile the System 🔍

**Add timing to each component:**

Update `RAG/query.py`:
```python
import time

def query(self, text: str, top_k: int = 5):
    times = {}
    
    # Retrieval
    start = time.time()
    context = self.rag.retrieve(text, top_k)
    times['retrieval'] = time.time() - start
    
    # Generation
    start = time.time()
    answer = self.gemini.generate_answer(text, context)
    times['generation'] = time.time() - start
    
    print(f"[TIMING] Retrieval: {times['retrieval']:.2f}s")
    print(f"[TIMING] Generation: {times['generation']:.2f}s")
    
    return result
```

## Quick Fixes (Immediate)

### Fix 1: Reduce top_k to 3
```python
# frontend/app.py, line 92
top_k = st.number_input("Results", min_value=1, max_value=10, value=3)
```

### Fix 2: Add timeout warning
```python
# frontend/app.py, line 95
if submit_button and query.strip():
    st.info("⏳ First query may take 10-15s (model loading). Subsequent queries will be faster.")
```

### Fix 3: Check backend logs
Look for slow operations in terminal running backend

## Expected Performance After Optimization

| Component | Before | After | Improvement |
|-----------|--------|-------|-------------|
| Embedding | 1s | 0.5s | 2x faster |
| Retrieval | 1s | 0.5s | 2x faster |
| Generation | 30s | 5s | 6x faster |
| **Total** | **34s** | **6-8s** | **4-5x faster** |

## Root Cause Analysis

**Most Likely Issues:**

1. **Gemini API Latency** (90% probability)
   - First request to Gemini is slow
   - Network latency
   - API cold start

2. **Too Many Chunks** (5% probability)
   - Sending too much context
   - Gemini processing time increases

3. **Model Reloading** (5% probability)
   - Embedding model reloading each time
   - Should be cached but might not be

## Recommended Actions

### Immediate (Do Now):
1. ✅ Reduce `top_k` from 5 to 3
2. ✅ Add timing logs to identify bottleneck
3. ✅ Check backend terminal for slow operations

### Short-term (This Week):
1. 🔧 Implement query caching
2. 🔧 Optimize Gemini API calls
3. 🔧 Consider using Gemini 1.5 Flash

### Long-term (Optional):
1. 🔮 Switch to local LLM (Ollama)
2. 🔮 Use GPU for embeddings
3. 🔮 Implement streaming responses

## Testing

**Run this test to identify bottleneck:**

```python
import time
import requests

# Test 1: Embedding + Retrieval only
start = time.time()
response = requests.get("http://localhost:8000/stats")
print(f"Health check: {time.time() - start:.2f}s")

# Test 2: Full query
start = time.time()
response = requests.post(
    "http://localhost:8000/query/text",
    json={"query": "test", "top_k": 1}
)
print(f"Full query: {time.time() - start:.2f}s")
```

**Expected Results:**
- Health check: < 1s
- Full query: 5-10s

**If full query > 20s:** Gemini API is the bottleneck

## Conclusion

**34s is too slow.** Expected is 5-10s.

**Most likely cause:** Gemini API latency

**Quick fix:** Reduce `top_k` to 3, add caching

**Long-term:** Consider local LLM or optimize Gemini calls
