# Requirements Document

## Introduction

Fluenta is an AI-powered English speaking practice platform. This spec covers the AI backend, built with Python and FastAPI, that powers real-time conversation coaching. The backend receives user speech as text from a React frontend, processes it through OpenAI (gpt-4o-mini), and returns AI replies, grammar corrections, follow-up questions, and realistic scores across four dimensions: fluency, grammar, pronunciation, and vocabulary.

The current backend has a single route with a global conversation history (not per-user) and hardcoded scores. This spec defines the requirements to evolve it into a modular, multi-user capable, production-ready AI backend.

## Glossary

- **Session**: A unique conversation context identified by a `session_id` string, scoped to one user.
- **AI_Service**: The service responsible for calling the OpenAI API and returning structured AI responses.
- **Conversation_Service**: The service responsible for storing and retrieving per-session conversation history.
- **Scoring_Service**: The service responsible for generating realistic scores from user input text.
- **Score**: An object containing numeric values (0–100) for fluency, grammar, pronunciation, and vocabulary, each with a short explanation.
- **Transcript_Service**: An optional service for converting audio input to text.
- **System_Prompt**: The initial instruction message sent to the OpenAI API that defines the AI coach persona and behavior.

---

## Requirements

### Requirement 1: Per-User Session Memory

**User Story:** As a language learner, I want my conversation history to be remembered within my session, so that the AI can give contextually relevant responses.

#### Acceptance Criteria

1. THE Conversation_Service SHALL store conversation history keyed by `session_id`.
2. WHEN a message is saved, THE Conversation_Service SHALL append the message with its role (`user` or `assistant`) to the session's history.
3. WHEN `get_history(session_id)` is called, THE Conversation_Service SHALL return all messages for that session in chronological order.
4. WHEN `clear_history(session_id)` is called, THE Conversation_Service SHALL remove all messages for that session.
5. WHILE multiple users are active simultaneously, THE Conversation_Service SHALL maintain isolated history for each `session_id` without cross-contamination.
6. IF a `session_id` has no existing history, THEN THE Conversation_Service SHALL return an empty list.

---

### Requirement 2: AI Response Generation

**User Story:** As a language learner, I want the AI to respond naturally, correct my grammar, and ask follow-up questions, so that I can practice real conversation.

#### Acceptance Criteria

1. WHEN a user message is received, THE AI_Service SHALL call the OpenAI API using the `gpt-4o-mini` model.
2. THE AI_Service SHALL include the last 10 messages of conversation history as context in each API call.
3. THE AI_Service SHALL use a System_Prompt that instructs the model to act as a friendly English coach named Fluenta.
4. THE AI_Service SHALL instruct the model to correct grammar mistakes with a short explanation.
5. THE AI_Service SHALL instruct the model to suggest vocabulary improvements when relevant.
6. THE AI_Service SHALL instruct the model to generate a follow-up question related to the user's last message.
7. THE AI_Service SHALL instruct the model to return a response in a structured JSON format containing `reply`, `correction`, `tip`, and `score` fields.
8. IF the OpenAI API call fails, THEN THE AI_Service SHALL raise an exception with a descriptive error message.
9. THE AI_Service SHALL use async functions compatible with FastAPI's async request handling.

---

### Requirement 3: Realistic Scoring

**User Story:** As a language learner, I want to receive realistic scores for my speaking, so that I can track my progress and understand my weaknesses.

#### Acceptance Criteria

1. WHEN a user sentence is provided, THE Scoring_Service SHALL return a Score object with numeric values between 0 and 100 for fluency, grammar, pronunciation, and vocabulary.
2. THE Scoring_Service SHALL derive scores from the content of the user's text, not return hardcoded values.
3. THE Scoring_Service SHALL include a short explanation (1 sentence) for each score dimension.
4. WHERE audio metrics are available (words per minute, pause count), THE Scoring_Service SHALL incorporate them into the fluency and pronunciation scores.
5. IF the input text is empty or whitespace-only, THEN THE Scoring_Service SHALL return a Score with all values set to 0 and explanations indicating no input was provided.
6. THE Scoring_Service SHALL produce scores that vary meaningfully across different quality inputs (e.g., a grammatically correct sentence scores higher on grammar than one with errors).

---

### Requirement 4: API Routes

**User Story:** As a frontend developer, I want clear and consistent API endpoints, so that I can integrate the AI backend into the React app.

#### Acceptance Criteria

1. THE Router SHALL expose a `POST /conversation` endpoint that accepts a `ConversationRequest` and returns a `ConversationResponse`.
2. WHEN `POST /conversation` is called, THE Router SHALL save the user message via Conversation_Service, call AI_Service, save the AI reply, and return the reply with scores.
3. THE Router SHALL expose a `GET /history` endpoint that accepts a `session_id` query parameter and returns the full conversation history for that session.
4. THE Router SHALL expose a `POST /evaluate` endpoint that accepts a text input and returns only a Score object without generating an AI reply.
5. IF a request body is malformed or missing required fields, THEN THE Router SHALL return an HTTP 422 response with validation details.
6. THE Router SHALL use async route handlers throughout.

---

### Requirement 5: Request and Response Schemas

**User Story:** As a developer, I want well-defined request and response schemas, so that the API contract is clear and validated automatically.

#### Acceptance Criteria

1. THE ConversationRequest schema SHALL contain a `session_id` field of type string and a `text` field of type string.
2. THE Score schema SHALL contain `fluency`, `grammar`, `pronunciation`, and `vocabulary` fields of type integer, each with an associated explanation string.
3. THE ConversationResponse schema SHALL contain a `reply` field of type string and a `score` field of type Score.
4. WHEN a request is received with a missing `session_id` or `text` field, THE Router SHALL return an HTTP 422 validation error.
5. THE schemas SHALL be defined using Pydantic and located in `backend/app/schemas/conversation_schema.py`.

---

### Requirement 6: Modular Service Architecture

**User Story:** As a backend developer, I want services to be clearly separated by concern, so that the codebase is maintainable and each service can be extended independently.

#### Acceptance Criteria

1. THE AI_Service SHALL not contain any conversation history storage logic.
2. THE Conversation_Service SHALL not contain any OpenAI API call logic.
3. THE Scoring_Service SHALL be callable independently of AI_Service (i.e., usable via the `/evaluate` route without triggering an AI reply).
4. THE Router SHALL orchestrate calls to Conversation_Service, AI_Service, and Scoring_Service without containing business logic itself.
5. THE System configuration (API keys, model name, max history length) SHALL be stored in `backend/app/config/settings.py` and imported by services that need them.

---

### Requirement 7: Configuration Management

**User Story:** As a developer, I want all configuration values centralized, so that I can change settings without hunting through multiple files.

#### Acceptance Criteria

1. THE Settings module SHALL read the `OPENAI_API_KEY` from environment variables.
2. THE Settings module SHALL define a configurable `MAX_HISTORY_LENGTH` value (default: 10) that controls how many messages are sent as context to the AI.
3. THE Settings module SHALL define the `OPENAI_MODEL` name (default: `gpt-4o-mini`).
4. IF the `OPENAI_API_KEY` environment variable is not set, THEN THE Settings module SHALL raise a descriptive configuration error at startup.
5. THE Settings module SHALL be located at `backend/app/config/settings.py`.

---

### Requirement 8: Audio Transcript Support (Optional Extension)

**User Story:** As a developer, I want an optional transcript service stub, so that audio-based scoring can be added later without restructuring the backend.

#### Acceptance Criteria

1. THE Transcript_Service SHALL expose a `transcribe(audio_bytes)` function that accepts raw audio bytes and returns a text string.
2. WHERE audio input is not available, THE Transcript_Service SHALL return an empty string without raising an error.
3. THE Transcript_Service SHALL be located at `backend/app/services/transcript_service.py` and be importable by routes without breaking existing functionality.
