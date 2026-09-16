from pydantic import BaseModel

class ResearchSource(BaseModel):

    source_type: str

    title: str

    locator: str | None = None

    abstract: str

    content: str