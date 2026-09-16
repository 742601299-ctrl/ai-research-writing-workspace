from pydantic import BaseModel

class Document(BaseModel):

    filename: str

    file_path: str

    text: str
