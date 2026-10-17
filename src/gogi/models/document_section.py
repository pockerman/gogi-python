from pydantic import BaseModel, Field


class DocumentSection(BaseModel):
    """A section of a document: a chapter or a heading within one, or a page of a PDF without an outline"""

    position: int = Field(..., description="1-based, in the order of the document; identifies the section")
    title: str = Field("", description="Empty for text before a document's first heading")
    level: int = Field(1, description="1 for a chapter, 2 for a heading within it, and so on")
    page_start: int | None = Field(None, description="The first page of a PDF the section is on")
    page_end: int | None = Field(None, description="The last page of a PDF the section is on")


class DocumentSectionContent(BaseModel):
    """A section with its own text, without its subsections'"""

    section: DocumentSection
    content: str
