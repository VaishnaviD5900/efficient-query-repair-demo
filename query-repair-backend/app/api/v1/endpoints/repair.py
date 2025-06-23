from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
async def ping():
    return {"message": "Repair endpoint is alive."}
