from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/app")
def frontend():
    return FileResponse("orderstack.html")
