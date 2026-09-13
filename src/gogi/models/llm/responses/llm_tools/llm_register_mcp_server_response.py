from typing import List

from pydantic import BaseModel


class LLMRegisterMcpServerResponse(BaseModel):
    imported_tool_names: List[str] = []
