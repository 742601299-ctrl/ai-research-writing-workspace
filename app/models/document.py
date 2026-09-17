from pydantic import BaseModel

class DocumentPage(BaseModel):

    page_number: int

    text: str

class Document(BaseModel):

    filename: str

    file_path: str

    text: str

    pages: list[DocumentPage]