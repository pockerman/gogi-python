from pydantic import BaseModel

from gogi.models.guardrails.triggered_rule import TriggeredRule


class ValidateInputResponse(BaseModel):
    allowed: bool = False
    denial_reason: str = ""
    triggered_checks: list[str] = []
    triggered_rules: list[TriggeredRule] = []
    # the message to show the user, from the rule that blocked or redirected the input
    user_message: str = ""
    evaluation_id: str = ""
