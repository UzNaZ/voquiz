from fastapi import APIRouter

menu_router = APIRouter()


@menu_router.get("/")
async def start():
    return
