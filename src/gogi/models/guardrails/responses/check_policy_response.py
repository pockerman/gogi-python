from typing import List

from pydantic import BaseModel


class CheckPolicyResponse(BaseModel):
    allowed: bool = False
    denial_reason: str = ""
    violated_rules: List[str] = []
    suggested_action: str = ""
