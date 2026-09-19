from openai import OpenAI

class EmbeddingService:

    def __init__(

        self,

        client: OpenAI,

        model: str = "text-embedding-3-small"

    ):

        self.client = client

        self.model = model

    def embed(

        self,

        texts: list[str]

    ) -> list[list[float]]:

        if not texts:

            return []

        response = self.client.embeddings.create(

            model=self.model,

            input=texts

        )

        return [

            item.embedding

            for item in response.data

        ]