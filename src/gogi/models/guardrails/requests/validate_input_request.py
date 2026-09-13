from typing import Dict, List

from pydantic import BaseModel


class ValidateInputRequest(BaseModel):
    content: str = ""
    checks: List[str] = []
    context: Dict[str, str] = {}
