"""
API Routes — orchestrates calls to conversation, AI, and scoring services.
Feature: fluenta-ai-backend
"""

from fastapi import APIRouter, HTTPException, Query

from app.services import conversation_service, ai_service, scoring_service
from app.services.ai_service import AIServiceError
from app.schemas.conversation_schema import (
    ConversationRequest,
    ConversationResponse,
    EvaluateRequest,
    HistoryMessage,
    HistoryResponse,
    Score,
)
from app.config.settings import MAX_HISTORY_LENGTH

router = APIRouter()


@router.post("/conversation", response_model=ConversationResponse)
async def conversation(data: ConversationRequest) -> ConversationResponse:
    try:
        conversation_service.save_message(data.session_id, "user", data.text)
        history = conversation_service.get_context_window(data.session_id, MAX_HISTORY_LENGTH)
        ai_result = await ai_service.get_ai_response(data.text, history)
        conversation_service.save_message(data.session_id, "assistant", ai_result["reply"])
        return ConversationResponse(
            reply=ai_result["reply"],
            correction=ai_result.get("correction", ""),
            tip=ai_result.get("tip", ""),
            score=ai_result["score"],
        )
    except AIServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/history", response_model=HistoryResponse)
async def get_history(session_id: str = Query(...)) -> HistoryResponse:
    messages = conversation_service.get_history(session_id)
    return HistoryResponse(
        session_id=session_id,
        messages=[HistoryMessage(role=m["role"], content=m["content"]) for m in messages],
    )


@router.post("/evaluate", response_model=Score)
async def evaluate(data: EvaluateRequest) -> Score:
    try:
        return await scoring_service.score_text(data.text)
    except AIServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
