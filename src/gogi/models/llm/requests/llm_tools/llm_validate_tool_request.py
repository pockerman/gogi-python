from pydantic import BaseModel


class LLMValidateToolRequest(BaseModel):
    tool_name: str
    arguments_json: str = ""
    # the version of the tool to validate against; empty uses the latest version
    version: str = ""
