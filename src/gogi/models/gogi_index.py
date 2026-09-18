from datetime import datetime

from pydantic import BaseModel


class GogiIndex(BaseModel):
    """A knowledge index with configuration and runtime stats"""

    index_id: str
    index_name: str
    owner: str
    created_at: datetime
    last_updated_at: datetime
