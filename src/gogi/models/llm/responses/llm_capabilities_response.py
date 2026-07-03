from pydantic import BaseModel 

from gogi.models.llm.llm_capabilities import LLMCapabilities

class LLMCapabilitiesResponse(BaseModel):
    capabilities: LLMCapabilities