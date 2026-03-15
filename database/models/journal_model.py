from database.connection import db
from datetime import datetime

def create_journal_entry(user_id, title, content):
    entry = {
        "user_id": user_id,
        "title": title,
        "content": content,
        "date": datetime.now(),
        "mood": "happy" # You can add more fields as the team builds the UI
    }
    return db.journals.insert_one(entry)

def get_user_journals(user_id):
    # This finds all journals for a specific person
    return list(db.journals.find({"user_id": user_id}))