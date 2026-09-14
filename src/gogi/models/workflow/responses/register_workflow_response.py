from pydantic import BaseModel


class RegisterWorkflowResponse(BaseModel):
    workflow_id: str = ""
    version: int = 0
