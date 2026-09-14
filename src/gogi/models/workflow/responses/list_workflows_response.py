from typing import List

from pydantic import BaseModel

from gogi.models.workflow.workflow_spec import WorkflowSpec


class ListWorkflowsResponse(BaseModel):
    specs: List[WorkflowSpec] = []
