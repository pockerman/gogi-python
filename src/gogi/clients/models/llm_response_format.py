from pydantic import BaseModel


class LLMRespnseFormat(BaseModel):
    response_type: str 
    schema_json: str