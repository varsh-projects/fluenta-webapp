import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    # 🔐 OpenAI Key (NEW - ADD THIS)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # 🗄️ MongoDB
    MONGO_URI = os.getenv("MONGO_URI")  # better than hardcoding
    DB_NAME = "fluenta"

    # ⚙️ App Settings
    DEBUG = True
    PORT = 5000

    # 📂 Collections
    USER_COLLECTION = "users"
    CONVO_COLLECTION = "conversations"
    SCORE_COLLECTION = "scores"