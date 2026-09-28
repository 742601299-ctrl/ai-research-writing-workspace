from pydantic import BaseModel, Field

class SearchWebArgs(BaseModel):

    query: str

    max_results: int = 5

class RetrieveLiteratureArgs(BaseModel):

    query: str

    top_k: int = 5

    source_ids: list[str] | None = None

class GetSourceArgs(BaseModel):

    source_id: str

class NewFindingInput(BaseModel):

    claim: str

    supporting_chunk_ids: list[str]

class NewGapInput(BaseModel):

    description: str

    supporting_finding_ids: list[str]

class NewGapResearchQuestionInput(BaseModel):

    question: str

    gap_ids: list[str]

class UpdateResearchStateArgs(BaseModel):

    new_findings: list[NewFindingInput] = Field(

        default_factory=list

    )

    new_gaps: list[NewGapInput] = Field(

        default_factory=list

    )

    new_gap_research_questions: list[NewGapResearchQuestionInput] = Field(

        default_factory=list

    )

    resolved_gap_ids: list[str] = Field(

        default_factory=list

    )