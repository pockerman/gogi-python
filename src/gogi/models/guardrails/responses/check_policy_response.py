from pydantic import BaseModel

from gogi.models.guardrails.triggered_rule import TriggeredRule


class CheckPolicyResponse(BaseModel):
    allowed: bool = False
    denial_reason: str = ""
    violated_rules: list[str] = []
    # what to do instead, e.g. require_approval when a human approval gate applies
    suggested_action: str = ""
    triggered_rules: list[TriggeredRule] = []
    # the role that must approve the action, if a human approval gate applies
    approval_role: str = ""
    evaluation_id: str = ""
