from datetime import datetime

def create_user(db, username, email=None):
    user = db.users.find_one({"username": username})

    if not user:
        db.users.insert_one({
            "username": username,
            "email": email,
            "created_at": datetime.utcnow(),
            "level": "beginner",
            "day1_score": None,
            "progress": [],
            "total_sessions": 0
        })


def update_user_progress(db, username, score):
    user = db.users.find_one({"username": username})

    # First session = Day 1 tracking
    if user["day1_score"] is None:
        db.users.update_one(
            {"username": username},
            {"$set": {"day1_score": score}}
        )

    # Store progress history
    db.users.update_one(
        {"username": username},
        {
            "$push": {"progress": score},
            "$inc": {"total_sessions": 1}
        }
    )

    # Level upgrade logic
    fluency = score["fluency"]

    if fluency >= 8:
        level = "advanced"
    elif fluency >= 5:
        level = "intermediate"
    else:
        level = "beginner"

    db.users.update_one(
        {"username": username},
        {"$set": {"level": level}}
    )