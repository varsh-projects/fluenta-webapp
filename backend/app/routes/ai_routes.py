from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ai_service import get_ai_response

router = APIRouter()

class ConversationRequest(BaseModel):
    text: str


@router.post("/conversation")
async def conversation(data: ConversationRequest):

    ai_reply = await get_ai_response(data.text)

    return {
        "reply": ai_reply
    }