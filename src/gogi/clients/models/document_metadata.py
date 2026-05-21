from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime, timezone


class DocumentMetadata(BaseModel):
    """Metadata tracked for each ingested document"""

    document_id: str
    index_name: str
    filename: str
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    chunk_count: int = 0
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    custom_metadata: Optional[Dict[str, str]] = None
