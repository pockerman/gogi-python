from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional

from gogi.clients.models.index_config import IndexConfig


class Index(BaseModel):
    """A knowledge index with configuration and runtime stats"""
    name: str
    config: IndexConfig
    owner: str = ""
    document_count: int = 0
    total_chunks: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_ingested_at: Optional[datetime] = None