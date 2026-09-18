from pydantic import BaseModel, Field


class IngestDocumentJob(BaseModel):
    job_id: str = Field(..., description="Unique identifier for the ingest document job")
    index_name: str = Field(..., description="Name of the index the document is being ingested into")
    document_id: str | None = Field(None, description="Identifier of the document being ingested (if available)")
    filename: str | None = Field(None, description="Original filename of the document being ingested")
    status: str = Field(
        ..., description="Current status of the ingest job (e.g., 'pending', 'in_progress', 'completed', 'failed')"
    )
    progress: float | None = Field(None, description="Progress of the ingest job as a percentage (0-100)")
    error_message: str | None = Field(None, description="Error message if the ingest job failed")


class IngestDocumentRequest(BaseModel):
    index_name: str
    filename: str
    document_id: str
    chunk_strategy: str
    embeddings_model: str
    embeddings_client: str
    batch_size: int = 10
    content: bytes
    content_type: str
    metadata: dict[str, str] | None = None
