from pydantic import BaseModel

<<<<<<< HEAD

class Message(BaseModel):
    role: str
    content: str
=======
class ConversationRequest(BaseModel):
    text: str
>>>>>>> af4e95dd02a2d2b5a105791fba3225d57800f849
