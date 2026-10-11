from pydantic import BaseModel

from gogi.models.guardrails.triggered_rule import TriggeredRule


class FilterOutputResponse(BaseModel):
    # the content to return to the user: redacted, or the rule's fallback if blocked
    content: str = ""
    modified: bool = False
    applied_filters: list[str] = []
    blocked: bool = False
    triggered_rules: list[TriggeredRule] = []
    evaluation_id: str = ""
