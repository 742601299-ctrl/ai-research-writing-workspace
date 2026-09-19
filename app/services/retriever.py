from app.models.retrieval import RetrievalResult

from app.services.embedding_service import EmbeddingService

from app.services.in_memory_vector_store import InMemoryVectorStore

class Retriever:

    def __init__(

        self,

        embedding_service: EmbeddingService,

        vector_store: InMemoryVectorStore

    ):

        self.embedding_service = embedding_service

        self.vector_store = vector_store

    def retrieve(

        self,

        query: str,

        top_k: int = 5,

        source_ids: list[str] | None = None

    ) -> list[RetrievalResult]:

        query_vector = self.embedding_service.embed(

            [query]

        )[0]

        return self.vector_store.search(

            query_vector=query_vector,

            top_k=top_k,

            source_ids=source_ids

        )