from .ai_routes import router as ai_router
from fastapi import APIRouter

router = APIRouter()

router.include_router(prefix="/ai", router=ai_router)
# router.include_router(prefix="/user", router=user_router)

