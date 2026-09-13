from typing import Dict

from pydantic import BaseModel


class ReportViolationRequest(BaseModel):
    policy_name: str = ""
    action: str = ""
    severity: str = ""
    context: Dict[str, str] = {}
    details: str = ""
