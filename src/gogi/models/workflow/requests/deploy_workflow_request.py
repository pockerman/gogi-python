from pydantic import BaseModel


class DeployWorkflowRequest(BaseModel):
    workflow_id: str = ""
    version: int = 0
    container_id: str = ""
    endpoint: str = ""
