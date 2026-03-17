from datetime import datetime

def save_score(db, username, scores):
    db.scores.insert_one({
        "username": username,
        "fluency": scores["fluency"],
        "grammar": scores["grammar"],
        "pronunciation": scores["pronunciation"],
        "vocabulary": scores["vocabulary"],
        "timestamp": datetime.utcnow()
    })


def get_user_scores(db, username):
    return list(db.scores.find({"username": username}))