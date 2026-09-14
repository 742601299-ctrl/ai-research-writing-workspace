from pydantic import BaseModel

class ResearchQuestion(BaseModel):

    question: str

    search_queries: list[str]

class ResearchPlan(BaseModel):

    topic: str

    objective: str

    research_questions: list[ResearchQuestion]