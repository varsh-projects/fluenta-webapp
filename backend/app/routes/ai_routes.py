from fastapi import APIRouter
from backend.app.schemas.conversation_schema import ConversationRequest
from backend.app.services.lesson_services import get_daily_lesson
from backend.app.services.ai_service import generate_ai_response
from backend.app.services.scoring_service import calculate_score
from backend.app.services.transcript_service import create_transcript

from database.connection import db

from database.models.user_model import create_user, update_user_progress
from database.models.conversation_model import save_conversation
from database.models.score_model import save_score

router = APIRouter()

@router.post("/conversation")
def conversation(req: ConversationRequest):

    create_user(db, req.username)

    user = db.users.find_one({"username": req.username})
    level = user.get("level", "beginner")

    # ✅ ADD HERE
    day = len(user.get("progress", [])) + 1
    lesson = get_daily_lesson(level, day)

    ai_response = generate_ai_response(req.text, level)

    transcript = create_transcript(req.text, ai_response)

    scores = calculate_score(req.text)

    save_conversation(db, req.username, transcript, ai_response, scores)
    save_score(db, req.username, scores)

    update_user_progress(db, req.username, scores)

    return {
        "ai_response": ai_response,
        "scores": scores,
        "level": level,
        "lesson": lesson,   # ✅ include this
        "day": day          # ✅ include this
    }