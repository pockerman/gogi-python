from typing import List

from pydantic import BaseModel


class WorkflowDeployment(BaseModel):
    workflow_id: str = ""
    deployment_id: str = ""
    version: int = 0
    status: str = ""
    current_replicas: int = 0
    desired_replicas: int = 0
    healthy_endpoints: List[str] = []
