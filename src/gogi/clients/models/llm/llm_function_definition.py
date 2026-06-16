from pydantic import BaseModel

class LLMFunctionDefinition(BaseModel):
    name: str
    description: str 
    parameters_json: str