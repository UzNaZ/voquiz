import fastapi

from .routes.quiz import quiz_router
from .routes.start_menu import menu_router

router = fastapi.APIRouter()
router.include_router(menu_router)
router.include_router(quiz_router)
