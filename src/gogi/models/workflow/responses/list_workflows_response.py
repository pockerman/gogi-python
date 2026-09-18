from pydantic import BaseModel

from gogi.models.workflow.workflow_spec import WorkflowSpec


class ListWorkflowsResponse(BaseModel):
    specs: list[WorkflowSpec] = []
