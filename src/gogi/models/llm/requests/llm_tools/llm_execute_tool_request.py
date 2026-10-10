from pydantic import BaseModel


class LLMExecuteToolRequest(BaseModel):
    tool_name: str
    arguments_json: str = ""
    session_id: str = ""
    # the version of the tool to run, e.g. "1.2.0"; empty runs the latest version
    version: str = ""
    # a human approved the call; required for tools whose behavior requires confirmation
    confirmed: bool = False
