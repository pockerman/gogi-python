from pydantic import BaseModel


class GetDeploymentStatusRequest(BaseModel):
    workflow_id: str = ""
