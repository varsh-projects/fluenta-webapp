from database.connection import db

def add_new_word(user_id, word, meaning):
    vocab = {
        "user_id": user_id,
        "word": word,
        "meaning": meaning,
        "mastered": False
    }
    return db.vocabulary.insert_one(vocab)