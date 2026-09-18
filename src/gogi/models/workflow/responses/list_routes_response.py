from pydantic import BaseModel

from gogi.models.workflow.route import Route


class ListRoutesResponse(BaseModel):
    routes: list[Route] = []
