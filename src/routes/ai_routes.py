import json
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field
from typing import Optional
import controllers.ai_controllers as ai_controllers


class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(default=None, description="Optional session ID for the chat")
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
async def ai_chat_route(request: ChatRequest, http_request: Request):
    session_id = http_request.headers.get('session_id')
    """Chat endpoint for AI service"""
    return ai_controllers.ai_chat_controller(request.message,f"{session_id}")



