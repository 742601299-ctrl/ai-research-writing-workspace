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

        # -------------------------------------------------

        # Validate query

        # -------------------------------------------------

        if not isinstance(query, str):

            raise ValueError(

                "Retrieval query must be a string."

            )

        query = query.strip()

        if not query:

            raise ValueError(

                "Retrieval query cannot be empty."

            )

        # -------------------------------------------------

        # Validate top_k

        # -------------------------------------------------

        if not isinstance(top_k, int) or isinstance(top_k, bool):

            raise ValueError(

                "top_k must be an integer."

            )

        if top_k <= 0:

            raise ValueError(

                "top_k must be greater than 0."

            )

        # -------------------------------------------------

        # Normalize source filters

        # -------------------------------------------------

        normalized_source_ids = None

        if source_ids is not None:

            if not isinstance(source_ids, list):

                raise ValueError(

                    "source_ids must be a list of source IDs or None."

                )

            normalized_source_ids = []

            for source_id in source_ids:

                if not isinstance(source_id, str):

                    raise ValueError(

                        "Every source_id must be a string."

                    )

                source_id = source_id.strip()

                if not source_id:

                    continue

                if source_id not in normalized_source_ids:

                    normalized_source_ids.append(source_id)

            # Treat [] as no source filter.

            if not normalized_source_ids:

                normalized_source_ids = None

        # -------------------------------------------------

        # Embed query

        # -------------------------------------------------

        query_vectors = self.embedding_service.embed(

            [query]

        )

        if not query_vectors:

            raise RuntimeError(

                "Embedding service returned no query vector."

            )

        query_vector = query_vectors[0]

        # -------------------------------------------------

        # Vector search

        # -------------------------------------------------

        results = self.vector_store.search(

            query_vector=query_vector,

            top_k=top_k,

            source_ids=normalized_source_ids

        )

        if results is None:

            return []

        # -------------------------------------------------

        # Defensive result validation

        # -------------------------------------------------

        validated_results: list[RetrievalResult] = []

        for result in results:

            if not isinstance(result, RetrievalResult):

                raise TypeError(

                    "Vector store returned an invalid retrieval result."

                )

            validated_results.append(result)

        return validated_results