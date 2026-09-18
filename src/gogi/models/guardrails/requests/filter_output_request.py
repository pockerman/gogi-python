from pydantic import BaseModel


class FilterOutputRequest(BaseModel):
    content: str = ""
    filters: list[str] = []
    context: dict[str, str] = {}
