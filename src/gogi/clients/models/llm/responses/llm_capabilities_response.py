from pydantic import BaseModel 

from gogi.clients.models.llm.llm_capabilities import LLMCapabilities

class LLMCapabilitiesResponse(BaseModel):
    capabilities: LLMCapabilities