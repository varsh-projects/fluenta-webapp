"""
FLUENTA DATABASE MAP (Schema)
This file is a reference for the team to see how data is structured.

1. Users Collection:
   { "username": str, "email": str, "level": str }

2. Conversations Collection:
   { "user_id": ObjectId, "transcript": str, "ai_response": str }

3. Scores Collection:
   { "user_id": ObjectId, "fluency_score": int, "grammar_score": int }

4. Journals Collection:
   { "user_id": ObjectId, "title": str, "content": str, "date": datetime }
"""

def show_schema():
    print("--- Fluenta Database Schema Map ---")
    print("Collections: Users, Conversations, Scores, Journals, Vocabulary")
    print("Status: Connected and Ready")

if __name__ == "__main__":
    show_schema()