from pydantic import BaseModel

from gogi.models.llm.llm_capabilities import LLMCapabilities 

class LLMModelInfo(BaseModel):
    name: str
    provider: str 
    capabilities: LLMCapabilities