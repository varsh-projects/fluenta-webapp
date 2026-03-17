from datetime import datetime

def save_conversation(db, username, transcript, ai_response, scores):
    db.conversations.insert_one({
        "username": username,
        "transcript": transcript,
        "ai_response": ai_response,
        "scores": scores,
        "timestamp": datetime.utcnow()
    })


def get_user_conversations(db, username):
    return list(db.conversations.find({"username": username}))