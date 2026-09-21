from pydantic import BaseModel

class SearchToolResult(BaseModel):

    source_id: str

    title: str

    source_type: str

    locator: str | None = None

    abstract: str

class RetrievalToolResult(BaseModel):

    source_id: str

    text: str

    page_start: int | None = None

    page_end: int | None = None

    similarity: float

class SourceDetailResult(BaseModel):

    source_id: str

    source_type: str

    title: str

    locator: str | None = None

    abstract: str