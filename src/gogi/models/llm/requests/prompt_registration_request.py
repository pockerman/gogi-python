from pydantic import BaseModel 
from typing import Dict


from gogi.models.prompts.prompt_metadata import PromptMetadata

class PromptRegistrationRequest(BaseModel):
    prompt_name: str
    prompt_version: str
    gogi_index: str
    content: bytes
    metadata: PromptMetadata