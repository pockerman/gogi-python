from pydantic import BaseModel

from gogi.models.workflow.workflow_spec import WorkflowSpec


class GetWorkflowResponse(BaseModel):
    spec: WorkflowSpec = WorkflowSpec()
