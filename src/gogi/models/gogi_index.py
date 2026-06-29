from pydantic import BaseModel, Field
from datetime import datetime, timezone

class GogiIndex(BaseModel):
    """A knowledge index with configuration and runtime stats"""
    index_id: str 
    index_name: str
    owner: str
    created_at: datetime 
    last_updated_at: datetime