from pydantic import BaseModel


class ReportViolationResponse(BaseModel):
    violation_id: str = ""
    recorded: bool = False
