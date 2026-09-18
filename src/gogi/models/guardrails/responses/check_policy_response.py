from pydantic import BaseModel


class CheckPolicyResponse(BaseModel):
    allowed: bool = False
    denial_reason: str = ""
    violated_rules: list[str] = []
    suggested_action: str = ""
