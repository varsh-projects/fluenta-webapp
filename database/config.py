import os

class Config:
    # 1. The main secret link to your MongoDB
    # In a real job, we'd use 'environment variables' here for safety
    MONGO_URI = "mongodb+srv://varshinisundhar2007_db_user:#computer25@fluenta.pv4evnd.mongodb.net/?retryWrites=true&w=majority&appName=fluenta"
    
    # 2. Database Name
    DB_NAME = "fluenta"
    
    # 3. App Settings
    DEBUG = True  # Set to False when the project is finished
    PORT = 5000   # The port your web app will run on
    
    # 4. Collection Names (so you don't make typos later!)
    USER_COLLECTION = "users"
    CONVO_COLLECTION = "conversations"
    SCORE_COLLECTION = "scores"