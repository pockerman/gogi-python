from pydantic import BaseModel

from gogi.models.workflow.workflow_job import WorkflowJob


class GetJobStatusResponse(BaseModel):
    job: WorkflowJob = WorkflowJob()
