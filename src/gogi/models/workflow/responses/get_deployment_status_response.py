from pydantic import BaseModel

from gogi.models.workflow.workflow_deployment import WorkflowDeployment


class GetDeploymentStatusResponse(BaseModel):
    deployment: WorkflowDeployment = WorkflowDeployment()
