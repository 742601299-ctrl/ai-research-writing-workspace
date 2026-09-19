from uuid import uuid4

from pydantic import BaseModel, Field

class ResearchSource(BaseModel):

    source_id: str = Field(

        default_factory=lambda: str(uuid4())

    )

    source_type: str

    title: str

    locator: str | None = None

    abstract: str

    content: str