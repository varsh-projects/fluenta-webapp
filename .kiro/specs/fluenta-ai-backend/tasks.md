# Implementation Plan: Fluenta AI Backend

## Overview

Incrementally build the modular AI backend for Fluenta, replacing the current single-file route with properly separated services, schemas, config, and tests. Each task builds on the previous one and ends with everything wired together.

## Tasks

- [x] 1. Set up config and project structure
  - Create `backend/app/config/__init__.py` and `backend/app/config/settings.py`
  - Read `OPENAI_API_KEY`, `OPENAI_MODEL` (default `gpt-4o-mini`), `MAX_HISTORY_LENGTH` (default 10) from environment
  - Raise `ValueError` at import time if `OPENAI_API_KEY` is missing
  - Create `backend/app/schemas/__init__.py` and `backend/app/schemas/conversation_schema.py` with all Pydantic schemas: `ConversationRequest`, `Score`, `ScoreExplanations`, `ConversationResponse`, `EvaluateRequest`, `HistoryMessage`, `HistoryResponse`
  - Update `backend/app/models/conversation.py` with the `Message` model
  - Add `hypothesis` and `pytest` to `backend/requirements.txt`
  - _Requirements: 5.1, 5.2, 5.3, 5.5, 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 2. Implement Conversation Service
  - [x] 2.1 Write `backend/app/services/conversation_service.py`
    - In-memory `_sessions` dict
    - Implement `get_history(session_id)`, `save_message(session_id, role, content)`, `clear_history(session_id)`, `get_context_window(session_id, n)`
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

  - [x] 2.2 Write property tests for Conversation Service
    - `backend/tests/test_conversation_service.py`
    - **Property 1: Session history round-trip** — save N messages, verify get_history returns them in order
    - **Property 2: Clear history is a reset** — save messages, clear, verify empty list
    - **Property 3: Session isolation** — save to session A, verify session B unchanged
    - Use `hypothesis` with `@given` and `@settings(max_examples=100)`
    - _Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [x] 3. Implement AI Service
  - [x] 3.1 Write `backend/app/services/ai_service.py`
    - Async `get_ai_response(user_text, history)` function
    - Build message list: system prompt + `history[-MAX_HISTORY_LENGTH:]` + current user message
    - Call `client.chat.completions.create` with `response_format={"type": "json_object"}`
    - Parse and return the JSON dict
    - Raise `AIServiceError` on API failure
    - System prompt must include: grammar correction, vocabulary tip, follow-up question, JSON output format
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9_

  - [x] 3.2 Write unit and property tests for AI Service
    - `backend/tests/test_ai_service.py`
    - **Property 4: Context window truncation** — for history length > MAX_HISTORY_LENGTH, verify only last N messages are included in the built message list (test the message list construction without calling the real API)
    - Unit test: system prompt contains required keywords (`correction`, `tip`, `follow-up`, `JSON`)
    - Unit test: `AIServiceError` raised when API call raises an exception (mock the client)
    - _Validates: Requirements 2.2, 2.3, 2.8_

- [x] 4. Checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement Scoring Service
  - [x] 5.1 Write `backend/app/services/scoring_service.py`
    - Async `score_text(user_text, context="")` function
    - If `user_text.strip()` is empty, return Score with all values 0 and explanations indicating no input
    - Otherwise, call OpenAI with a scoring-focused prompt requesting JSON with fluency/grammar/pronunciation/vocabulary scores and explanations
    - Parse response and return a `Score` Pydantic model
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [x] 5.2 Write property tests for Scoring Service
    - `backend/tests/test_scoring_service.py`
    - **Property 5: Score shape invariant** — for any non-empty text, all four scores are in [0, 100] and all explanations are non-empty strings (use `hypothesis` with `st.text(min_size=1)`)
    - Edge case within Property 5: whitespace-only strings return all zeros
    - **Property 6: Score variation** — a grammatically correct sentence scores >= an erroneous sentence on grammar (use two fixed example strings)
    - _Validates: Requirements 3.1, 3.2, 3.3, 3.5, 3.6_

- [x] 6. Implement Transcript Service stub
  - Write `backend/app/services/transcript_service.py`
  - `transcribe(audio_bytes: bytes) -> str` returns `""` for any input
  - _Requirements: 8.1, 8.2, 8.3_

- [x] 7. Implement API Routes
  - [x] 7.1 Rewrite `backend/app/routes/ai_routes.py`
    - Import and use `conversation_service`, `ai_service`, `scoring_service`
    - `POST /conversation`: save user message → get context window → call ai_service → save assistant reply → return `ConversationResponse`
    - `GET /history`: return `HistoryResponse` for given `session_id`
    - `POST /evaluate`: call `scoring_service.score_text` only, return `Score`
    - All handlers must be `async`
    - Return HTTP 503 if `AIServiceError` is raised
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 6.1, 6.2, 6.3, 6.4_

  - [x] 7.2 Write unit tests for routes
    - `backend/tests/test_routes.py`
    - Use FastAPI `TestClient`
    - Test `POST /conversation` returns correct response shape
    - Test `GET /history` returns empty list for unknown session
    - Test `POST /evaluate` returns Score shape
    - Test missing `session_id` or `text` returns HTTP 422
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.4_

- [x] 8. Final checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Each task references specific requirements for traceability
- Property tests use `hypothesis` with `@settings(max_examples=100)`
- The real OpenAI API is not called in unit/property tests — mock `client.chat.completions.create` where needed
- `transcript_service` is a stub; no tests required beyond import verification
