from uuid import uuid4

from pydantic import BaseModel, Field

class TraceableEvidence(BaseModel):

    evidence_id: str = Field(

        default_factory=lambda: str(uuid4())

    )

    chunk_id: str

    source_id: str