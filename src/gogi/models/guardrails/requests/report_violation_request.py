from pydantic import BaseModel


class ReportViolationRequest(BaseModel):
    policy_name: str = ""
    action: str = ""
    severity: str = ""
    context: dict[str, str] = {}
    details: str = ""
