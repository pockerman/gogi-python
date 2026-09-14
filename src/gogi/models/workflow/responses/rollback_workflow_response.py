from pydantic import BaseModel

from gogi.models.workflow.workflow_deployment import WorkflowDeployment


class RollbackWorkflowResponse(BaseModel):
    deployment: WorkflowDeployment = WorkflowDeployment()
