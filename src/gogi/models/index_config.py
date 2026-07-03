from pydantic import BaseModel
from typing import Optional, Dict


class IndexConfig(BaseModel):
    """Configuration for creating an index"""

    name: str
    embedding_model: str
    embedding_dimensions: int
    chunking_strategy: str
    chunk_size: int
    chunk_overlap: int
    metadata_schema: Optional[Dict] | None = None