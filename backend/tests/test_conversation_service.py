"""
Property-based tests for conversation_service.
Feature: fluenta-ai-backend
"""

import pytest
from hypothesis import given, settings, strategies as st, HealthCheck

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import backend.app.services.conversation_service as svc


def _reset():
    """Clear all sessions between tests."""
    svc._sessions.clear()


# ---------------------------------------------------------------------------
# Property 1: Session history round-trip
# Save N messages, verify get_history returns them in order with correct roles.
# Validates: Requirements 1.1, 1.2, 1.3
# ---------------------------------------------------------------------------

ROLES = st.sampled_from(["user", "assistant"])

@given(
    session_id=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"))),
    messages=st.lists(
        st.fixed_dictionaries({
            "role": ROLES,
            "content": st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs"))),
        }),
        min_size=1,
        max_size=10,
    ),
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_property1_session_history_round_trip(session_id, messages):
    # Feature: fluenta-ai-backend, Property 1: Session history round-trip
    _reset()
    for msg in messages:
        svc.save_message(session_id, msg["role"], msg["content"])

    history = svc.get_history(session_id)

    assert len(history) == len(messages)
    for saved, original in zip(history, messages):
        assert saved["role"] == original["role"]
        assert saved["content"] == original["content"]


# Edge case: unknown session_id returns empty list (Requirement 1.6)
def test_property1_edge_unknown_session_returns_empty():
    _reset()
    assert svc.get_history("nonexistent-session-xyz") == []


# ---------------------------------------------------------------------------
# Property 2: Clear history is a reset
# Save messages, clear, verify empty list.
# Validates: Requirements 1.4
# ---------------------------------------------------------------------------

@given(
    session_id=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"))),
    messages=st.lists(
        st.fixed_dictionaries({
            "role": ROLES,
            "content": st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs"))),
        }),
        min_size=1,
        max_size=10,
    ),
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_property2_clear_history_is_reset(session_id, messages):
    # Feature: fluenta-ai-backend, Property 2: Clear history is a reset
    _reset()
    for msg in messages:
        svc.save_message(session_id, msg["role"], msg["content"])

    svc.clear_history(session_id)

    assert svc.get_history(session_id) == []


# ---------------------------------------------------------------------------
# Property 3: Session isolation
# Save to session A, verify session B is unchanged.
# Validates: Requirements 1.5
# ---------------------------------------------------------------------------

@given(
    session_a=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"))),
    session_b=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"))),
    messages_a=st.lists(
        st.fixed_dictionaries({
            "role": ROLES,
            "content": st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs"))),
        }),
        min_size=1,
        max_size=5,
    ),
    messages_b=st.lists(
        st.fixed_dictionaries({
            "role": ROLES,
            "content": st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs"))),
        }),
        min_size=0,
        max_size=5,
    ),
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_property3_session_isolation(session_a, session_b, messages_a, messages_b):
    # Feature: fluenta-ai-backend, Property 3: Session isolation
    from hypothesis import assume
    assume(session_a != session_b)

    _reset()

    # Populate session B first, record its state
    for msg in messages_b:
        svc.save_message(session_b, msg["role"], msg["content"])
    snapshot_b = svc.get_history(session_b)

    # Now write to session A
    for msg in messages_a:
        svc.save_message(session_a, msg["role"], msg["content"])

    # Session B must be unchanged
    assert svc.get_history(session_b) == snapshot_b
