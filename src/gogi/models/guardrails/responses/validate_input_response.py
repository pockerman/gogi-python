from typing import List

from pydantic import BaseModel


class ValidateInputResponse(BaseModel):
    allowed: bool = False
    denial_reason: str = ""
    triggered_checks: List[str] = []
