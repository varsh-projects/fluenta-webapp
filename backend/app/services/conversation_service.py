"""
Conversation Service — manages per-session in-memory message history.
"""

from typing import List

# Internal store: keyed by session_id
_sessions: dict[str, List[dict]] = {}


def get_history(session_id: str) -> List[dict]:
    """Return all messages for a session in chronological order.
    Returns an empty list if the session has no history."""
    return list(_sessions.get(session_id, []))


def save_message(session_id: str, role: str, content: str) -> None:
    """Append a message with the given role to the session's history."""
    if session_id not in _sessions:
        _sessions[session_id] = []
    _sessions[session_id].append({"role": role, "content": content})


def clear_history(session_id: str) -> None:
    """Remove all messages for the given session."""
    _sessions.pop(session_id, None)


def get_context_window(session_id: str, n: int) -> List[dict]:
    """Return the last n messages for the session (for use as OpenAI context)."""
    history = _sessions.get(session_id, [])
    return list(history[-n:]) if n > 0 else []
