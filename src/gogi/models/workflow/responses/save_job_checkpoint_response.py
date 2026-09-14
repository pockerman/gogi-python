from pydantic import BaseModel


class SaveJobCheckpointResponse(BaseModel):
    success: bool = False
