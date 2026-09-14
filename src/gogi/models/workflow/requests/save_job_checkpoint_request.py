from pydantic import BaseModel


class SaveJobCheckpointRequest(BaseModel):
    job_id: str = ""
    checkpoint_json: str = ""
