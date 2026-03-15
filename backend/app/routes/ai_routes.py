from fastapi import APIRouter
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter()

conversation_history = [
    {
        "role": "system",
        "content": """
You are Fluenta, an AI English speaking partner.
Your job is to talk naturally with the user and help improve their fluency.

Rules:
1. Continue the conversation like a real human.
2. Ask follow-up questions.
3. If the user makes grammar mistakes, correct them politely.
4. Keep replies short (2–3 sentences) so it feels like natural conversation.
"""
    }
]

class ConversationRequest(BaseModel):
    text: str


@router.post("/conversation")
async def conversation(data: ConversationRequest):

    user_text = data.text

    conversation_history.append({
        "role": "user",
        "content": user_text
    })

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation_history
    )

    ai_reply = response.choices[0].message.content

    conversation_history.append({
        "role": "assistant",
        "content": ai_reply
    })

    return {
        "reply": ai_reply,
        "score": {
            "fluency": 80,
            "grammar": 75,
            "pronunciation": 70,
            "vocabulary": 72
        }
    }