from pydantic import BaseModel, Field


class EmbeddingModel(BaseModel):
    """A text embedding model the application can ingest and search documents with: one gogi provides, or one
    the application hosts and registered by its URL."""

    name: str = Field(..., description="e.g. 'bge-small-en-v1.5'")
    dimensions: int = Field(0, description="the length of its vectors")
    max_input_tokens: int = Field(0, description="the most tokens it reads; a document's chunks for it are shorter")
    url: str = Field("", description="where the application's own model is; empty for the models gogi provides")
    credential_ref: str = Field("", description="the credential it is called with, e.g. 'openai'; empty if none")
    available: bool = Field(True, description="false for OpenAI's model until the application stores its key")
