def add_new_word(db, username, word, meaning):
    db.vocabulary.insert_one({
        "username": username,
        "word": word,
        "meaning": meaning,
        "mastered": False
    })


def mark_word_mastered(db, username, word):
    db.vocabulary.update_one(
        {"username": username, "word": word},
        {"$set": {"mastered": True}}
    )


def get_user_words(db, username):
    return list(db.vocabulary.find({"username": username}))