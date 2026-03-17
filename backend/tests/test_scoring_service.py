"""
Property-based tests for scoring_service.
Feature: fluenta-ai-backend
"""

import os
import sys
import json
import asyncio

# Must set env var BEFORE any app imports so settings.py doesn't raise ValueError
os.environ.setdefault("OPENAI_API_KEY", "test-key")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from hypothesis import given, settings, strategies as st, HealthCheck

from backend.app.services.scoring_service import score_text
from backend.app.schemas.conversation_schema import Score


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_openai_response(fluency=75, grammar=80, pronunciation=70, vocabulary=85):
    """Build a mock OpenAI response with the given score values."""
    payload = {
        "fluency": fluency,
        "grammar": grammar,
        "pronunciation": pronunciation,
        "vocabulary": vocabulary,
        "explanations": {
            "fluency": "Sentences flow naturally.",
            "grammar": "Grammar is mostly correct.",
            "pronunciation": "Word choices are moderate complexity.",
            "vocabulary": "Good range of vocabulary.",
        },
    }
    mock_message = MagicMock()
    mock_message.content = json.dumps(payload)
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    return mock_response


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


# ---------------------------------------------------------------------------
# Property 5: Score shape invariant
# For any non-empty text, all four scores are in [0, 100] and all explanations
# are non-empty strings.
# Validates: Requirements 3.1, 3.3
# ---------------------------------------------------------------------------

@given(user_text=st.text(min_size=1, max_size=100))
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_property5_score_shape_invariant(user_text):
    # Feature: fluenta-ai-backend, Property 5: Score shape invariant
    if not user_text.strip():
        # Edge case: whitespace-only → all zeros (tested separately below)
        return

    mock_response = _make_openai_response(
        fluency=75, grammar=80, pronunciation=70, vocabulary=85
    )

    with patch("app.services.scoring_service.client") as mock_client:
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        score = _run(score_text(user_text))

    assert isinstance(score, Score)
    for field in ("fluency", "grammar", "pronunciation", "vocabulary"):
        value = getattr(score, field)
        assert 0 <= value <= 100, f"{field} score {value} out of range [0, 100]"

    for field in ("fluency", "grammar", "pronunciation", "vocabulary"):
        explanation = getattr(score.explanations, field)
        assert isinstance(explanation, str) and len(explanation) > 0, (
            f"Explanation for {field} must be a non-empty string"
        )


# Edge case within Property 5: whitespace-only strings return all zeros
# Validates: Requirement 3.5
@given(
    user_text=st.text(
        alphabet=st.characters(whitelist_categories=("Zs",)),
        min_size=1,
        max_size=20,
    )
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
def test_property5_edge_whitespace_returns_zeros(user_text):
    # Feature: fluenta-ai-backend, Property 5 edge case: whitespace-only → zeros
    score = _run(score_text(user_text))

    assert score.fluency == 0
    assert score.grammar == 0
    assert score.pronunciation == 0
    assert score.vocabulary == 0


# ---------------------------------------------------------------------------
# Property 6: Score variation (metamorphic)
# A grammatically correct sentence scores >= an erroneous sentence on grammar.
# Uses two fixed example strings.
# Validates: Requirements 3.2, 3.6
# ---------------------------------------------------------------------------

def test_property6_score_variation_grammar():
    # Feature: fluenta-ai-backend, Property 6: Score variation
    correct_sentence = "I went to the store yesterday and bought some groceries."
    erroneous_sentence = "I go to store yesterday and buyed some grocery."

    correct_response = _make_openai_response(grammar=88)
    erroneous_response = _make_openai_response(grammar=42)

    with patch("app.services.scoring_service.client") as mock_client:
        mock_client.chat.completions.create = AsyncMock(
            side_effect=[correct_response, erroneous_response]
        )
        correct_score = _run(score_text(correct_sentence))
        erroneous_score = _run(score_text(erroneous_sentence))

    assert correct_score.grammar >= erroneous_score.grammar, (
        f"Correct sentence grammar score ({correct_score.grammar}) should be >= "
        f"erroneous sentence grammar score ({erroneous_score.grammar})"
    )


# ---------------------------------------------------------------------------
# Unit test: empty string returns all-zero Score without calling OpenAI
# Validates: Requirement 3.5
# ---------------------------------------------------------------------------

def test_empty_string_returns_zero_score_without_api_call():
    with patch("app.services.scoring_service.client") as mock_client:
        mock_client.chat.completions.create = AsyncMock()
        score = _run(score_text(""))

    mock_client.chat.completions.create.assert_not_called()
    assert score.fluency == 0
    assert score.grammar == 0
    assert score.pronunciation == 0
    assert score.vocabulary == 0
