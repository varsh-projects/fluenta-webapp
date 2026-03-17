from openai import OpenAI
from backend.app.config.settings import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_ai_response(user_text, level="beginner"):
    
    if level == "beginner":
        system_prompt = "Talk in simple English. Correct mistakes politely."
    elif level == "intermediate":
        system_prompt = "Talk normally. Give slight corrections."
    else:
        system_prompt = "Speak fluently. Challenge the user with complex sentences."

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ]
    )

    return response.choices[0].message.content