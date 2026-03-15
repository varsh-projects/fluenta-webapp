from pydantic import BaseModel

class ConversationRequest(BaseModel):
    text: str