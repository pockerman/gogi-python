from pydantic import BaseModel


class RegisterRouteRequest(BaseModel):
    api_path: str = ""
    endpoint: str = ""
