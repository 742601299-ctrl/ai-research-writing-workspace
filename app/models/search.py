from pydantic import BaseModel

class SearchResult(BaseModel):

    title: str

    url: str

    content: str

    raw_content: str | None = None


class ResearchQuestionResult(BaseModel):

    research_question: str

    search_query: str

    search_results: list[SearchResult]