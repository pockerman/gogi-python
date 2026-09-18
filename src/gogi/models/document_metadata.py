from datetime import UTC, datetime

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Metadata tracked for each ingested document"""

    document_id: str
    index_name: str
    filename: str
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    chunk_count: int = 0
    page_count: int | None = None
    word_count: int | None = None
    custom_metadata: dict[str, str] | None = None
