#!/bin/bash
# Starts the FastAPI backend and Streamlit frontend together (for Mac/Linux).
# On Windows, just run the two commands in separate terminals instead.

echo "Starting FastAPI backend on http://localhost:8000 ..."
uvicorn legalEaseAPI.main:app --reload &
BACKEND_PID=$!

sleep 2

echo "Starting Streamlit frontend on http://localhost:8501 ..."
streamlit run frontend/app.py

kill $BACKEND_PID
