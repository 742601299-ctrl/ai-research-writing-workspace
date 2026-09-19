from pydantic import BaseModel

class ResearchChunk(BaseModel):

    chunk_id: str

    source_id: str

    text: str

    page_start: int | None = None

    page_end: int | None = None