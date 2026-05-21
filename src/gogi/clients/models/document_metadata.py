from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional, Dict


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
