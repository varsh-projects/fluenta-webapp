"""
Unit tests for API routes.
Feature: fluenta-ai-backend
"""

import os
import sys

# Set env var before any app imports so settings.py doesn't raise ValueError
os.environ.setdefault("OPENAI_API_KEY", "test-key")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
import app.services.conversation_service as conv_svc

client = TestClient(app)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MOCK_AI_RESULT = {
    "reply": "Great effort! What do you enjoy most about school?",
    "correction": "You should say 'I went to school yesterday'.",
    "tip": "Consider using 'attended' for a more formal tone.",
    "score": {
        "fluency": 75,
        "grammar": 60,
        "pronunciation": 70,
        "vocabulary": 72,
        "explanations": {
            "fluency": "Mostly natural flow.",
            "grammar": "Incorrect past tense used.",
            "pronunciation": "Moderate complexity.",
            "vocabulary": "Good everyday range.",
        },
    },
}

MOCK_SCORE = {
    "fluency": 80,
    "grammar": 85,
    "pronunciation": 78,
    "vocabulary": 82,
    "explanations": {
        "fluency": "Smooth and natural.",
        "grammar": "No errors found.",
        "pronunciation": "Clear word choices.",
        "vocabulary": "Varied vocabulary.",
    },
}


def _make_score_obj():
    from app.schemas.conversation_schema import Score, ScoreExplanations
    return Score(
        fluency=MOCK_SCORE["fluency"],
        grammar=MOCK_SCORE["grammar"],
        pronunciation=MOCK_SCORE["pronunciation"],
        vocabulary=MOCK_SCORE["vocabulary"],
        explanations=ScoreExplanations(**MOCK_SCORE["explanations"]),
    )


@pytest.fixture(autouse=True)
def clear_sessions():
    """Reset conversation state between tests."""
    conv_svc._sessions.clear()
    yield
    conv_svc._sessions.clear()


# ---------------------------------------------------------------------------
# POST /conversation — correct response shape
# Validates: Requirements 4.1, 4.2
# ---------------------------------------------------------------------------

def test_post_conversation_returns_correct_shape():
    with patch(
        "app.routes.ai_routes.ai_service.get_ai_response",
        new=AsyncMock(return_value=MOCK_AI_RESULT),
    ):
        response = client.post(
            "/conversation",
            json={"session_id": "sess-1", "text": "I go to school yesterday."},
        )

    assert response.status_code == 200
    body = response.json()
    assert "reply" in body
    assert "correction" in body
    assert "tip" in body
    assert "score" in body
    score = body["score"]
    for field in ("fluency", "grammar", "pronunciation", "vocabulary", "explanations"):
        assert field in score


# ---------------------------------------------------------------------------
# GET /history — empty list for unknown session
# Validates: Requirement 4.3
# ---------------------------------------------------------------------------

def test_get_history_unknown_session_returns_empty():
    response = client.get("/history", params={"session_id": "unknown-session"})
    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == "unknown-session"
    assert body["messages"] == []


# ---------------------------------------------------------------------------
# GET /history — returns saved messages
# Validates: Requirement 4.3
# ---------------------------------------------------------------------------

def test_get_history_returns_saved_messages():
    conv_svc.save_message("sess-hist", "user", "Hello")
    conv_svc.save_message("sess-hist", "assistant", "Hi there!")

    response = client.get("/history", params={"session_id": "sess-hist"})
    assert response.status_code == 200
    body = response.json()
    assert len(body["messages"]) == 2
    assert body["messages"][0] == {"role": "user", "content": "Hello"}
    assert body["messages"][1] == {"role": "assistant", "content": "Hi there!"}


# ---------------------------------------------------------------------------
# POST /evaluate — returns Score shape
# Validates: Requirement 4.4
# ---------------------------------------------------------------------------

def test_post_evaluate_returns_score_shape():
    with patch(
        "app.routes.ai_routes.scoring_service.score_text",
        new=AsyncMock(return_value=_make_score_obj()),
    ):
        response = client.post("/evaluate", json={"text": "I love learning English."})

    assert response.status_code == 200
    body = response.json()
    for field in ("fluency", "grammar", "pronunciation", "vocabulary", "explanations"):
        assert field in body
    assert 0 <= body["fluency"] <= 100
    assert 0 <= body["grammar"] <= 100


# ---------------------------------------------------------------------------
# Missing required fields → HTTP 422
# Validates: Requirements 4.5, 5.4
# ---------------------------------------------------------------------------

def test_post_conversation_missing_session_id_returns_422():
    response = client.post("/conversation", json={"text": "Hello"})
    assert response.status_code == 422


def test_post_conversation_missing_text_returns_422():
    response = client.post("/conversation", json={"session_id": "sess-1"})
    assert response.status_code == 422


def test_post_evaluate_missing_text_returns_422():
    response = client.post("/evaluate", json={})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# POST /conversation — HTTP 503 on AIServiceError
# Validates: Requirement 4.6 (error handling)
# ---------------------------------------------------------------------------

def test_post_conversation_returns_503_on_ai_error():
    from app.services.ai_service import AIServiceError

    with patch(
        "app.routes.ai_routes.ai_service.get_ai_response",
        new=AsyncMock(side_effect=AIServiceError("API down")),
    ):
        response = client.post(
            "/conversation",
            json={"session_id": "sess-err", "text": "Hello"},
        )

    assert response.status_code == 503
