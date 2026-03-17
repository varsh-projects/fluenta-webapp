from pydantic import BaseModel

class ConversationRequest(BaseModel):
    username: str
    text: str