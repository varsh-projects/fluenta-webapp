import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are Fluenta, an AI English speaking partner.

Talk naturally with the user and help improve English fluency.

Rules:
- Keep replies short (2–3 sentences)
- Ask follow-up questions
- Correct grammar politely
"""

async def get_ai_response(user_text: str):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ]
    )

    return response.choices[0].message.content