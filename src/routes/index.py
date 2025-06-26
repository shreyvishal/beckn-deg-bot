from .ai_routes import router as ai_router
from .auth_routes import router as auth_router
from fastapi import APIRouter

router = APIRouter()

router.include_router(prefix="/ai", router=ai_router)
router.include_router(prefix="/auth", router=auth_router)

