from pydantic import BaseModel, Field
import datetime
from typing import Optional, Dict


class DocumentMetadata(BaseModel):
    """Metadata tracked for each ingested document"""

    document_id: str
    index_name: str
    filename: str
    ingested_at: datetime = Field(default_factory=datetime.datetime.now)
    chunk_count: int = 0
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    custom_metadata: Optional[Dict[str, str]] = None
