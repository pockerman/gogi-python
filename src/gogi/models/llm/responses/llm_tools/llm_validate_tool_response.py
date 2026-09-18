from pydantic import BaseModel


class LLMValidateToolResponse(BaseModel):
    valid: bool
    errors: list[str] = []
