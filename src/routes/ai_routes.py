from fastapi import APIRouter, Request
from pydantic import BaseModel, Field
from typing import Optional
import controllers.ai_controllers as ai_controllers


class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(default=None, description="Optional session ID for the chat")
    message: str = Field(..., description="The message to send to the AI")


# Create router
router = APIRouter()

@router.get("/health" )
async def ai_health_check_route():
    """Health check endpoint for AI service"""
    return ai_controllers.ai_health_check_controller()


@router.post("/chat")
async def ai_chat_route(request: ChatRequest, http_request: Request):
    session_id = http_request.headers.get('session_id')
    """Chat endpoint for AI service"""
    return ai_controllers.ai_chat_controller(request.message,f"{session_id}")



