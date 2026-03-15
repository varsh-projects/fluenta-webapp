import os
from openai import OpenAI

# create AI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_speech(text):

    prompt = f"""
You are Fluenta AI, an English speaking coach.

A learner said this sentence:
"{text}"

Do the following:

1. Reply naturally to continue the conversation.
2. Correct the sentence if it has grammar mistakes.
3. Give one tip to improve the sentence.

Also score the learner:

Fluency: 0-100
Grammar: 0-100
Pronunciation: 0-100
Vocabulary: 0-100

Return ONLY in this JSON format:

{{
"reply": "...",
"correction": "...",
"tip": "...",
"score": {{
"fluency": number,
"grammar": number,
"pronunciation": number,
"vocabulary": number
}}
}}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return {
        "reply": response.output_text,
        "score": {
            "fluency": 80,
            "grammar": 75,
            "pronunciation": 70,
            "vocabulary": 72
        }
    }