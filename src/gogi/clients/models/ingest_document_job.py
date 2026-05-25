from pydantic import BaseModel, Field
from typing import Optional


class IngestDocumentJob(BaseModel):
    job_id: str = Field(..., description="Unique identifier for the ingest document job")
    index_name: str = Field(..., description="Name of the index the document is being ingested into")
    document_id: Optional[str] = Field(None, description="Identifier of the document being ingested (if available)")
    filename: Optional[str] = Field(None, description="Original filename of the document being ingested")
    status: str = Field(..., description="Current status of the ingest job (e.g., 'pending', 'in_progress', 'completed', 'failed')")
    progress: Optional[float] = Field(None, description="Progress of the ingest job as a percentage (0-100)")
    error_message: Optional[str] = Field(None, description="Error message if the ingest job failed")
