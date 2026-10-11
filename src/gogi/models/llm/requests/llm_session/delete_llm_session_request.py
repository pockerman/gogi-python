from pydantic import BaseModel


class DeleteLLMSessionRequest(BaseModel):
    session_id: str
    # also delete the memories saved for this session; the user's own memories are kept
    delete_memories: bool = False
