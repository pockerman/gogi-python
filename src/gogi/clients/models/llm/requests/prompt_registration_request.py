from pydantic import BaseModel 

class PromptRegistrationRequest(BaseModel):
    prompt_id: str