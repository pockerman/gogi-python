from pydantic import BaseModel

from gogi.clients.models.llm.llm_model_info import LLMModelInfo

class LLMRegisterRequest(BaseModel):
    info: LLMModelInfo
    endpoint: str 
    health_check: str 
    adapter_type: str 

