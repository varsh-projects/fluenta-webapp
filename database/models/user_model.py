from database.connection import db
from datetime import datetime

def create_user(username, email, password):
    user_data = {
        "username": username,
        "email": email,
        "password": password, # In a real app, you'd hash this!
        "created_at": datetime.now(),
        "level": "Beginner"
    }
    return db.users.insert_one(user_data)

def get_user(username):
    return db.users.find_one({"username": username})