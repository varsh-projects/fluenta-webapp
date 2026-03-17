def create_transcript(user_text, ai_text):
    return [
        {"speaker": "user", "text": user_text},
        {"speaker": "ai", "text": ai_text}
    ]