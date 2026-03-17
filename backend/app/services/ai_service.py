from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_ai_response(text, level):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # ✅ updated working model
            messages=[
                {"role": "system", "content": f"You are a helpful assistant for a {level} user."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        print("ERROR:", e)
        return f"AI error: {str(e)}"