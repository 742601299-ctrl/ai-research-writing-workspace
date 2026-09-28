from uuid import uuid4

from pydantic import BaseModel, Field

from app.models.traceable_evidence import TraceableEvidence

class Finding(BaseModel):

    finding_id: str = Field(

        default_factory=lambda: str(uuid4())

    )

    claim: str

    evidence_ids: list[str]

class ResearchGap(BaseModel):

    gap_id: str = Field(

        default_factory=lambda: str(uuid4())

    )

    description: str

    supporting_finding_ids: list[str]

class GapResearchQuestion(BaseModel):

    question_id: str = Field(

        default_factory=lambda: str(uuid4())

    )

    question: str

    gap_ids: list[str]

class ResearchState(BaseModel):

    evidence: list[TraceableEvidence] = Field(

        default_factory=list

    )

    findings: list[Finding] = Field(

        default_factory=list

    )

    gaps: list[ResearchGap] = Field(

        default_factory=list

    )

    gap_research_questions: list[GapResearchQuestion] = Field(

        default_factory=list

    )