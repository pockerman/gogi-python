from pydantic import BaseModel


class PromptDeleteRequest(BaseModel):
    prompt_id: str