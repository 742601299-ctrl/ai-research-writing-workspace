import math

from app.models.research_chunk import ResearchChunk

from app.models.retrieval import RetrievalResult

class InMemoryVectorStore:

    def __init__(self):

        self._items: list[

            tuple[ResearchChunk, list[float]]

        ] = []

    def add(

        self,

        chunks: list[ResearchChunk],

        vectors: list[list[float]]

    ) -> None:

        if len(chunks) != len(vectors):

            raise ValueError(

                "chunks and vectors must have the same length"

            )

        for chunk, vector in zip(

            chunks,

            vectors

        ):

            self._items.append(

                (chunk, vector)

            )

    def search(

        self,

        query_vector: list[float],

        top_k: int = 5,

        source_ids: list[str] | None = None

    ) -> list[RetrievalResult]:

        results = []

        for chunk, vector in self._items:

            if (

                source_ids is not None

                and chunk.source_id not in source_ids

            ):

                continue

            similarity = self._cosine_similarity(

                query_vector,

                vector

            )

            results.append(

                RetrievalResult(

                    chunk=chunk,

                    similarity=similarity

                )

            )

        results.sort(

            key=lambda result: result.similarity,

            reverse=True

        )

        return results[:top_k]

    def _cosine_similarity(

        self,

        vector_a: list[float],

        vector_b: list[float]

    ) -> float:

        dot_product = sum(

            a * b

            for a, b in zip(

                vector_a,

                vector_b

            )

        )

        magnitude_a = math.sqrt(

            sum(

                a * a

                for a in vector_a

            )

        )

        magnitude_b = math.sqrt(

            sum(

                b * b

                for b in vector_b

            )

        )

        if magnitude_a == 0 or magnitude_b == 0:

            return 0.0

        return dot_product / (

            magnitude_a * magnitude_b

        )