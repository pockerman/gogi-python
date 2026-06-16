from pydantic import BaseModel

class LLMCapabilities(BaseModel):
    context_window: int 
    supports_vision: bool
    supports_tools: bool
    supports_streaming: bool
    supports_json_mode: bool
