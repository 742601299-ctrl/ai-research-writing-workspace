from pydantic import BaseModel

class ResearchPlan(BaseModel):

    topic: str

    objective: str

    questions: list[str]