from pydantic import BaseModel

from gogi.models.workflow.workflow_spec import WorkflowSpec


class UpdateWorkflowRequest(BaseModel):
    spec: WorkflowSpec = WorkflowSpec()
