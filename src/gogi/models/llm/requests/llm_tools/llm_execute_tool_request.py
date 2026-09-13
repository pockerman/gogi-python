from pydantic import BaseModel


class LLMExecuteToolRequest(BaseModel):
    tool_name: str
    arguments_json: str = ""
    session_id: str = ""
