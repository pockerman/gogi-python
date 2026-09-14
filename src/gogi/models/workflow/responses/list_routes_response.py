from typing import List

from pydantic import BaseModel

from gogi.models.workflow.route import Route


class ListRoutesResponse(BaseModel):
    routes: List[Route] = []
