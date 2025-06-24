from fastapi import APIRouter
from pydantic import BaseModel
import controllers.ai_controllers as ai_controllers




# Create router
ai_router = APIRouter(prefix="/ai", tags=["AI"])

@ai_router.get("/health" )
async def ai_health_check_route():
    """Health check endpoint for AI service"""
    return ai_controllers.ai_health_check_controller()




