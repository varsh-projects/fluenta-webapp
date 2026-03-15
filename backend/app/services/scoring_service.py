"""
Scoring Service — generates realistic scores from user text via OpenAI.
Feature: fluenta-ai-backend
"""

import json
from openai import AsyncOpenAI, OpenAIError

from app.config.settings import OPENAI_API_KEY, OPENAI_MODEL
from app.schemas.conversation_schema import Score, ScoreExplanations

client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

SCORING_PROMPT = """You are an English language evaluator. Evaluate the following text and return scores.

Score each dimension from 0 to 100:
- fluency: sentence flow, naturalness, word order
- grammar: correctness of tense, agreement, articles
- pronunciation: word-choice complexity and common mispronunciation risk (text proxy)
- vocabulary: range and appropriateness of words used

For each dimension, also provide a short 1-sentence explanation.

Return ONLY valid JSON in this exact format:
{
  "fluency": <int 0-100>,
  "grammar": <int 0-100>,
  "pronunciation": <int 0-100>,
  "vocabulary": <int 0-100>,
  "explanations": {
    "fluency": "...",
    "grammar": "...",
    "pronunciation": "...",
    "vocabulary": "..."
  }
}"""

_EMPTY_SCORE = Score(
    fluency=0,
    grammar=0,
    pronunciation=0,
    vocabulary=0,
    explanations=ScoreExplanations(
        fluency="No input was provided.",
        grammar="No input was provided.",
        pronunciation="No input was provided.",
        vocabulary="No input was provided.",
    ),
)


async def score_text(user_text: str, context: str = "") -> Score:
    """
    Score the given user text across four dimensions.

    Returns a Score with all zeros if user_text is empty or whitespace-only.
    Raises AIServiceError on OpenAI API failure.
    """
    if not user_text.strip():
        return _EMPTY_SCORE

    prompt = SCORING_PROMPT
    if context:
        prompt += f"\n\nConversation context:\n{context}"

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_text},
    ]

    try:
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        return Score(
            fluency=int(data["fluency"]),
            grammar=int(data["grammar"]),
            pronunciation=int(data["pronunciation"]),
            vocabulary=int(data["vocabulary"]),
            explanations=ScoreExplanations(
                fluency=data["explanations"]["fluency"],
                grammar=data["explanations"]["grammar"],
                pronunciation=data["explanations"]["pronunciation"],
                vocabulary=data["explanations"]["vocabulary"],
            ),
        )
    except OpenAIError as exc:
        from app.services.ai_service import AIServiceError
        raise AIServiceError(f"Scoring API call failed: {exc}") from exc
    except (json.JSONDecodeError, KeyError, IndexError, ValueError) as exc:
        from app.services.ai_service import AIServiceError
        raise AIServiceError(f"Failed to parse scoring response: {exc}") from exc
