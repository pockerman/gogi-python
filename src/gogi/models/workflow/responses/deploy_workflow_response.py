from pydantic import BaseModel

from gogi.models.workflow.workflow_deployment import WorkflowDeployment


class DeployWorkflowResponse(BaseModel):
    deployment: WorkflowDeployment = WorkflowDeployment()
