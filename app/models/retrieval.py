from pydantic import BaseModel

from app.models.research_chunk import ResearchChunk

class RetrievalResult(BaseModel):

    chunk: ResearchChunk

    similarity: float