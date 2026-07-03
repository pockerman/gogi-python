from pydantic import BaseModel 


from gogi.models.llm.llm_model_info import LLMModelInfo

class RegisteredLLM(BaseModel):
    info: LLMModelInfo
    endpoint: str
    health_check: str 
    status: str 
    registered_at: str 
    adapter_type: str
