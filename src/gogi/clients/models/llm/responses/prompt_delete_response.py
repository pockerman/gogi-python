from pydantic import BaseModel


class PromptDeleteResponse(BaseModel):
    deleted: bool