from database.connection import db
from datetime import datetime

def save_score(user_id, fluency_score, grammar_score):
    score_entry = {
        "user_id": user_id,
        "fluency_score": fluency_score, # e.g., 85
        "grammar_score": grammar_score, # e.g., 70
        "date": datetime.now()
    }
    return db.scores.insert_one(score_entry)