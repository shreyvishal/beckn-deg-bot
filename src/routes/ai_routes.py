import json

from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel, Field
from typing import Optional
import controllers.ai_controllers as ai_controllers
from middleware.auth_middleware import get_current_active_user
from models.user import UserResponse


class ChatRequest(BaseModel):
    message: str = Field(..., description="The message to send to the AI")


# Create router
router = APIRouter()

@router.post("/health" )
async def ai_health_check_route(http_request: Request):
    data = await http_request.body()
    data = json.loads(data)
    print("data-----> ",data)
    """Health check endpoint for AI service"""
    return ai_controllers.ai_health_check_controller(data["session_id"])


@router.post("/chat")
async def ai_chat_route(
    request: ChatRequest, 
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Chat endpoint for AI service - requires authentication"""
    # Use user ID as session ID for user-specific conversations
    user_session_id = f"user_{current_user.id}"
    return ai_controllers.ai_chat_controller(request.message, user_session_id)



