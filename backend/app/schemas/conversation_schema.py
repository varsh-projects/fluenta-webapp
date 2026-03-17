from pydantic import BaseModel
from typing import List


class ConversationRequest(BaseModel):
    username: str
    text: str


class ScoreExplanations(BaseModel):
    fluency: str
    grammar: str
    pronunciation: str
    vocabulary: str


class Score(BaseModel):
    fluency: int
    grammar: int
    pronunciation: int
    vocabulary: int
    explanations: ScoreExplanations


class ConversationResponse(BaseModel):
    reply: str
    correction: str
    tip: str
    score: Score


class EvaluateRequest(BaseModel):
    text: str


class HistoryMessage(BaseModel):
    role: str
    content: str


class HistoryResponse(BaseModel):
    session_id: str
    messages: List[HistoryMessage]
