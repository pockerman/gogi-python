from pydantic import BaseModel


class ReportViolationRequest(BaseModel):
    policy_name: str = ""
    action: str = ""
    # low (default), medium, high, critical or blocked
    severity: str = ""
    context: dict[str, str] = {}
    details: str = ""
    # the evaluation that found the violation, if any
    evaluation_id: str = ""
