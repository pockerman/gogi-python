from pydantic import BaseModel


class CancelJobResponse(BaseModel):
    success: bool = False
