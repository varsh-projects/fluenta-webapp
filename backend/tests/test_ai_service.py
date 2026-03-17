"""
Unit and property-based tests for ai_service.
Feature: fluenta-ai-backend
"""

import json
import os
import sys

# Must set env var BEFORE any app imports so settings.py doesn't raise ValueError
os.environ.setdefault("OPENAI_API_KEY", "test-key")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import AsyncMock, patch
from hypothesis import given, settings, strategies as st, HealthCheck

from backend.app.services.ai_service import (
    _build_messages,
    get_ai_response,
    AIServiceError,
    SYSTEM_PROMPT,
)
from backend.app.config.settings import MAX_HISTORY_LENGTH


# ---------------------------------------------------------------------------
# Unit test: system prompt contains required keywords
# Validates: Requirement 2.3, 2.4, 2.5, 2.6, 2.7
# ---------------------------------------------------------------------------

def test_system_prompt_contains_required_keywords():
    prompt_lower = SYSTEM_PROMPT.lower()
    assert "correction" in prompt_lower, "System prompt must mention 'correction'"
    assert "tip" in prompt_lower, "System prompt must mention 'tip'"
    assert "follow-up" in prompt_lower, "System prompt must mention 'follow-up'"
    assert "json" in prompt_lower, "System prompt must mention 'JSON'"


# ---------------------------------------------------------------------------
# Property 4: Context window truncation
# For history length > MAX_HISTORY_LENGTH, verify only last N messages are
# included in the built message list (plus the system prompt).
# Validates: Requirement 2.2
# ---------------------------------------------------------------------------

@given(
    user_text=st.text(min_size=1, max_size=50),
    history=st.lists(
        st.fixed_dictionaries({
            "role": st.sampled_from(["user", "assistant"]),
            "content": st.text(min_size=1, max_size=50),
        }),
        min_size=MAX_HISTORY_LENGTH + 1,
        max_size=MAX_HISTORY_LENGTH + 20,
    ),
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_property4_context_window_truncation(user_text, history):
    # Feature: fluenta-ai-backend, Property 4: Context window truncation
    messages = _build_messages(user_text, history)

    # messages = [system_prompt] + history[-MAX_HISTORY_LENGTH:] + [user_message]
    # so total = 1 + MAX_HISTORY_LENGTH + 1
    assert len(messages) == MAX_HISTORY_LENGTH + 2

    # First message is the system prompt
    assert messages[0]["role"] == "system"

    # Last message is the current user text
    assert messages[-1]["role"] == "user"
    assert messages[-1]["content"] == user_text

    # The history slice must be the last MAX_HISTORY_LENGTH messages
    expected_history_slice = history[-MAX_HISTORY_LENGTH:]
    actual_history_slice = messages[1:-1]
    assert actual_history_slice == expected_history_slice


# ---------------------------------------------------------------------------
# Unit test: AIServiceError raised when API call raises an exception
# Validates: Requirement 2.8
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ai_service_error_on_api_failure():
    from openai import OpenAIError

    mock_response = AsyncMock(side_effect=OpenAIError("connection error"))

    with patch("app.services.ai_service.client") as mock_client:
        mock_client.chat.completions.create = mock_response
        with pytest.raises(AIServiceError, match="OpenAI API call failed"):
            await get_ai_response("Hello", [])


# ---------------------------------------------------------------------------
# Unit test: _build_messages with history <= MAX_HISTORY_LENGTH keeps all
# ---------------------------------------------------------------------------

def test_build_messages_short_history_kept_in_full():
    history = [
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello!"},
    ]
    messages = _build_messages("How are you?", history)
    # system + 2 history + user = 4
    assert len(messages) == 4
    assert messages[1] == history[0]
    assert messages[2] == history[1]
    assert messages[-1]["content"] == "How are you?"
