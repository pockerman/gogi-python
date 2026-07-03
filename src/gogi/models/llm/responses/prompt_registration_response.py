from pydantic import BaseModel

class PromptRegistrationResponse(BaseModel):
    prompt_id: str