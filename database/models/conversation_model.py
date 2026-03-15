from database.connection import db
from datetime import datetime

def save_conversation(user_id, transcript, ai_response):
    conversation = {
        "user_id": user_id,
        "transcript": transcript,
        "ai_response": ai_response,
        "timestamp": datetime.now()
    }
    return db.conversations.insert_one(conversation)