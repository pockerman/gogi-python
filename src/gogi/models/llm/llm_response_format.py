from pydantic import BaseModel


class LLMRespnseFormat(BaseModel):
    response_type: str 
    response_schema_json: str