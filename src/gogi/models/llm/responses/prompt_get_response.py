from pydantic import BaseModel 


from gogi.models.prompts.prompt_metadata import PromptMetadata


class PromptGetResponse(BaseModel):
    prompt_id: str
    prompt_name: str
    prompt_version: str
    gogi_index: str
    content: bytes
    metadata: PromptMetadata