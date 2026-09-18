from pydantic import BaseModel


class AddMMessagesToLLMSessionResponse(BaseModel):
    success: bool
    message_count: int
