from pydantic import BaseModel


class Violation(BaseModel):
    """A policy violation an application reported."""

    violation_id: str = ""
    policy_name: str = ""
    action: str = ""
    severity: str = ""
    context: dict[str, str] = {}
    details: str = ""
    evaluation_id: str = ""
    # unix millis
    created_at: int = 0
