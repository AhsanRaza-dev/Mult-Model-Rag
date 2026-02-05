# FixIt.AI Frontend

Streamlit web interface for the FixIt.AI machinery repair assistant.

## Features

- 💬 Text query input
- 📖 Answer display with formatting
- 📚 Source citations with page numbers
- 📊 System statistics sidebar
- 📝 Example questions
- 📜 Query history
- ⚡ Real-time response times

## Running the Frontend

### Prerequisites

Make sure the backend is running:
```bash
cd backend
uvicorn app.main:app --reload
```

### Start Streamlit

```bash
cd frontend
streamlit run app.py
```

The app will open at: http://localhost:8501

## Usage

1. Enter your question in the text area
2. Click "Ask Question" or press Ctrl+Enter
3. View the answer and source citations
4. Check query history for previous questions

## Example Questions

- How do I replace the brake pads?
- What are the torque specifications for the wheel bolts?
- How do I check the oil level?
- What is the tire pressure specification?
- How do I replace the air filter?

## Configuration

The app connects to the backend at `http://localhost:8000` by default.

To change this, edit `app.py`:
```python
API_URL = "http://your-backend-url:8000"
```

## Deployment

### Streamlit Cloud (Free)

1. Push to GitHub
2. Go to https://streamlit.io/cloud
3. Connect your repository
4. Deploy!

### Docker

```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Local Network

```bash
streamlit run app.py --server.address=0.0.0.0
```

Access from other devices: `http://your-ip:8501`

## Troubleshooting

**Backend Offline Error:**
- Make sure backend is running on port 8000
- Check `http://localhost:8000/health`

**Connection Timeout:**
- Query might be taking too long
- Check backend logs for errors

**No Results:**
- Verify backend has indexed documents
- Check `/stats` endpoint shows documents > 0
