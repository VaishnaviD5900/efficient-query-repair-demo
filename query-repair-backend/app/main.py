# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router

app = FastAPI(
    title="Efficient Query Repair API",
    description="A web-based tool for SQL query repair with aggregate constraints using Full Filtering and Range Pruning algorithms.",
    version="1.0.0"
)

# Optional: allow frontend (e.g., React) to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all v1 API routes
app.include_router(api_router, prefix="/api/v1")
