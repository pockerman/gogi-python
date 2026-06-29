from pydantic import BaseModel


class PromptGetRequest(BaseModel):
    prompt_id: str