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
    # the metadata the document was ingested with; each of its chunks has it too
    custom_metadata: dict[str, str] | None = None
    content_type: str | None = None
    # the status of the document's ingestion job, e.g. PENDING, COMPLETED or FAILED
    status: str | None = None
    job_id: str | None = None
