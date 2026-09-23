import json

from pydantic import BaseModel

class SearchToolResult(BaseModel):

    source_id: str

    title: str

    source_type: str

    locator: str | None = None

    abstract: str

class RetrievalToolResult(BaseModel):

    chunk_id: str

    source_id: str

    text: str

    page_start: int | None = None

    page_end: int | None = None

    similarity: float

class SourceDetailResult(BaseModel):

    source_id: str

    source_type: str

    title: str

    locator: str | None = None

    abstract: str

class ToolExecutionResult(BaseModel):

    success: bool

    tool_name: str

    data: object | None = None

    error: str | None = None

    def to_observation(self) -> str:

        return json.dumps(

            self.model_dump(),

            ensure_ascii=False

        )