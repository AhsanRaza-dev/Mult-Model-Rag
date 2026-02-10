
# Deployment Guide

## Prerequisites
- Docker Installed
- Access to `.env` variables

## Build and Run

1. **Build the image**:
   ```bash
   docker-compose build
   ```

2. **Run the services**:
   ```bash
   docker-compose up
   ```

3. **Access**:
   - Web Interface: http://localhost:8501
   - API Docs: http://localhost:8000/docs

## Cloud Deployment (Example: Hugging Face Spaces)

1. Create a new Space (Docker SDK).
2. Upload the `Dockerfile` and all project files.
3. Set Secrets (`GEMINI_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`) in Space settings.
4. The Space will build and run automatically.

## Notes
- The Docker image includes Tesseract OCR for PDF processing.
- Both Streamlit and FastAPI run in the same container for simplicity in this configuration. For production scaling, split them into separate services in `docker-compose.yml`.
