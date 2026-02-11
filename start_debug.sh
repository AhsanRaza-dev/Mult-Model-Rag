#!/bin/bash
echo "Starting backend..." > start.log
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 >> start.log 2>&1 &
BACKEND_PID=$!

echo "Starting frontend..." >> start.log
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0 >> start.log 2>&1 &
FRONTEND_PID=$!

echo "Backend PID: $BACKEND_PID" >> start.log
echo "Frontend PID: $FRONTEND_PID" >> start.log

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
