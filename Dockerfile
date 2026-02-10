
# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (Tesseract OCR)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage cache
COPY requirements.txt .
COPY frontend/requirements.txt requirements-frontend.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r requirements-frontend.txt

# Copy application code
COPY . .

# Expose ports
EXPOSE 8000
EXPOSE 8501

# Create a startup script
RUN echo '#!/bin/bash\n\
    uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 & \n\
    streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0 \n\
    wait' > start.sh && chmod +x start.sh

# Environment variables (to be overridden at runtime)
ENV GEMINI_API_KEY=""
ENV QDRANT_URL=""
ENV QDRANT_API_KEY=""

# Start command
CMD ["./start.sh"]
