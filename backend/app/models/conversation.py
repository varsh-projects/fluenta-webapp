from datetime import datetime

def save_conversation(db, username, transcript, scores):
    db.conversations.insert_one({
        "username": username,
        "transcript": transcript,
        "scores": scores,
        "timestamp": datetime.utcnow()
    })