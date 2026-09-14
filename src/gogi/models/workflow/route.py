from pydantic import BaseModel


class Route(BaseModel):
    api_path: str = ""
    endpoint: str = ""
