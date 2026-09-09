from pydantic import BaseModel


class LLMValidateToolRequest(BaseModel):
    tool_name: str
    arguments_json: str = ""
