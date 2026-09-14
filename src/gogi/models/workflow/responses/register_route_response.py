from pydantic import BaseModel


class RegisterRouteResponse(BaseModel):
    success: bool = False
