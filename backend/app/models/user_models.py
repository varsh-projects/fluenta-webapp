from datetime import datetime

def create_user(db, username):
    existing = db.users.find_one({"username": username})

    if not existing:
        db.users.insert_one({
            "username": username,
            "created_at": datetime.utcnow(),
            "level": "beginner",
            "day1_score": None
        })

def update_user_progress(db, username, score):
    user = db.users.find_one({"username": username})

    if user["day1_score"] is None:
        db.users.update_one(
            {"username": username},
            {"$set": {"day1_score": score}}
        )
    else:
        # Improve level based on score
        if score["fluency"] > 7:
            level = "advanced"
        elif score["fluency"] > 4:
            level = "intermediate"
        else:
            level = "beginner"

        db.users.update_one(
            {"username": username},
            {"$set": {"level": level}}
        )