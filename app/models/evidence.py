from pydantic import BaseModel

from app.models.research_source import ResearchSource

class Evidence(BaseModel):

    research_question: str

    source: ResearchSource

    relevance: float

class EvidenceRelevanceResult(BaseModel):

    relevance: float