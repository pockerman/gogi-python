from pydantic import BaseModel

from gogi.models.workflow.workflow_spec import WorkflowSpec


class RegisterWorkflowRequest(BaseModel):
    spec: WorkflowSpec = WorkflowSpec()
