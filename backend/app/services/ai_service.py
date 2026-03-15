"""
AI Service — calls OpenAI and returns a structured coaching response.
Feature: fluenta-ai-backend
"""

import json
from openai import AsyncOpenAI, OpenAIError

from app.config.settings import OPENAI_API_KEY, OPENAI_MODEL, MAX_HISTORY_LENGTH

client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

SYSTEM_PROMPT = """You are Fluenta, a friendly and encouraging English speaking coach.

For every user message you MUST:
1. Reply naturally to continue the conversation (field: "reply").
2. Correct any grammar mistakes with a short explanation (field: "correction"). If there are no mistakes, say "No correction needed."
3. Suggest one vocabulary improvement when relevant (field: "tip"). If none, say "No tip needed."
4. Ask one follow-up question at the end of your reply to keep the conversation going.

Also evaluate the user's English and return scores 0-100 for:
- fluency: sentence flow and naturalness
- grammar: correctness of tense, agreement, articles
- pronunciation: word-choice complexity and common mispronunciation risk
- vocabulary: range and appropriateness of words used

Return ONLY valid JSON in this exact format:
{
  "reply": "...",
  "correction": "...",
  "tip": "...",
  "score": {
    "fluency": <int>,
    "grammar": <int>,
    "pronunciation": <int>,
    "vocabulary": <int>,
    "explanations": {
      "fluency": "...",
      "grammar": "...",
      "pronunciation": "...",
      "vocabulary": "..."
    }
  }
}"""


class AIServiceError(Exception):
    """Raised when the OpenAI API call fails."""


def _build_messages(user_text: str, history: list[dict]) -> list[dict]:
    truncated_history = history[-MAX_HISTORY_LENGTH:]
    return (
        [{"role": "system", "content": SYSTEM_PROMPT}]
        + truncated_history
        + [{"role": "user", "content": user_text}]
    )


async def get_ai_response(user_text: str, history: list[dict]) -> dict:
    messages = _build_messages(user_text, history)
    try:
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except OpenAIError as exc:
        raise AIServiceError(f"OpenAI API call failed: {exc}") from exc
    except (json.JSONDecodeError, KeyError, IndexError) as exc:
        raise AIServiceError(f"Failed to parse OpenAI response: {exc}") from exc
