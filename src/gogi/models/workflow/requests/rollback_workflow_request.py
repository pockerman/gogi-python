from pydantic import BaseModel


class RollbackWorkflowRequest(BaseModel):
    workflow_id: str = ""
    target_version: int = 0
