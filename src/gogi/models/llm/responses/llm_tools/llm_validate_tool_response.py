from typing import List

from pydantic import BaseModel


class LLMValidateToolResponse(BaseModel):
    valid: bool
    errors: List[str] = []
