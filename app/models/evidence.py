from pydantic import BaseModel

class Evidence(BaseModel):

    research_question: str

    title: str

    url: str

    abstract: str

    relevance: float

class EvidenceRelevanceResult(BaseModel):

    relevance: float