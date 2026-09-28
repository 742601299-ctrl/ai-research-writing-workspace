from pydantic import BaseModel

class Citation(BaseModel):

    citation_number: int

    source_id: str

    title: str

    source_type: str

    locator: str | None = None