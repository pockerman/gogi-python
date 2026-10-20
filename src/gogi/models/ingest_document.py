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
    # chosen by the platform if empty
    document_id: str = ""
    chunk_strategy: str = "fixed"
    # the models that embed the document's chunks, each into a collection of its own, e.g.
    # ["bge-small-en-v1.5"]; with none the document is only stored, e.g. a video, and can be ingested later
    embedding_models: list[str] = Field(default_factory=list)
    batch_size: int = 10
    content: bytes
    content_type: str
    metadata: dict[str, str] | None = None
    # replace the content of the existing document of document_id, e.g. after it was edited
    replace: bool = False


class IngestStoredDocumentRequest(BaseModel):
    """Chunks a document the index already has and embeds it with the models; ingesting again with a model
    replaces what that model embedded of it, and keeps what other models embedded"""

    index_name: str
    document_id: str
    embedding_models: list[str] = Field(..., min_length=1)
    chunk_strategy: str = "fixed"
    batch_size: int = 10
