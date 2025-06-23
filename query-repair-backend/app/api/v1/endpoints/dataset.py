# app/api/v1/endpoints/dataset.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
async def ping():
    return {"message": "Dataset endpoint is alive."}
