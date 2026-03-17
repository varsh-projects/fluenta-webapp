from datetime import datetime

def create_journal_entry(db, username, title, content, mood=None):
    db.journals.insert_one({
        "username": username,
        "title": title,
        "content": content,
        "mood": mood,
        "timestamp": datetime.utcnow()
    })


def get_user_journals(db, username):
    return list(db.journals.find({"username": username}))