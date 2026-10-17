from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class IndexRole(StrEnum):
    """What a member of an index may do with it."""

    # changes the index's documents and members
    OWNER = "owner"
    # reads and searches the index's documents
    READER = "reader"


class GogiIndex(BaseModel):
    """A knowledge index with configuration and runtime stats"""

    index_id: str
    index_name: str
    # the user who created the index
    owner: str
    created_at: datetime
    last_updated_at: datetime
    members: dict[str, IndexRole] = Field(
        default_factory=dict, description="Everyone with a role, the creator included"
    )
