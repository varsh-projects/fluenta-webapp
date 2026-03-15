from pymongo import MongoClient
from config import Config # Import your settings
import certifi

# Now we use the variable from config.py instead of the long messy string
client = MongoClient(Config.MONGO_URI, tlsCAFile=certifi.where())
db = client[Config.DB_NAME]

print(f"Connected to {Config.DB_NAME} using settings from config.py!")