from pydantic import BaseModel


class AddMMessagesToLLMSessionResponse(BaseModel):
    success: bool
    # the number of messages added
    message_count: int
    # the number of messages of the session
    total_count: int = 0
