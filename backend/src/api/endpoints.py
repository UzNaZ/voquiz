import fastapi

from routes.start_menu import menu_router

router = fastapi.APIRouter()
router.include_router(menu_router)
