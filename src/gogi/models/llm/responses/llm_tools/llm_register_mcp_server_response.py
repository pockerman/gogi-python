from pydantic import BaseModel


class LLMRegisterMcpServerResponse(BaseModel):
    imported_tool_names: list[str] = []
