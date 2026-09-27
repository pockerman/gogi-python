from pydantic import BaseModel, Field


class SearchDocumentsRequest(BaseModel):
    """Similarity search over the chunks stored in an index"""

    index_name: str
    query: str
    top_k: int = Field(5, gt=0, description="Maximum number of chunks to return")
    embeddings_model: str = Field(..., description="Must match the model the documents were ingested with")
    embeddings_client: str = Field(..., description="Must match the client the documents were ingested with")
    document_ids: list[str] | None = Field(None, description="Restrict the search to these documents")
    metadata_filter: dict[str, str] | None = Field(None, description="Exact-match filters on the chunk metadata")


class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    index_name: str
    content: str
    score: float = Field(..., description="Similarity between the chunk and the query; higher is more similar")
    metadata: dict[str, str] | None = None


class SearchDocumentsResponse(BaseModel):
    chunks: list[DocumentChunk] = Field(default_factory=list)
