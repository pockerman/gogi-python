from pydantic import BaseModel


class CreateJobResponse(BaseModel):
    job_id: str = ""
