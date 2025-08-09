# app/api/v1/api.py

from fastapi import APIRouter
from app.api.v1.endpoints import dataset, query, repair

api_router = APIRouter()
api_router.include_router(repair.router, prefix="/repair", tags=["Repair"])
