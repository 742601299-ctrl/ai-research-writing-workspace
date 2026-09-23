from app.models.research_source import ResearchSource

from app.services.in_memory_vector_store import InMemoryVectorStore

class ResearchWorkspace:

    def __init__(

        self,

        vector_store: InMemoryVectorStore

    ):

        self.vector_store = vector_store

        self._sources: dict[

            str,

            ResearchSource

        ] = {}

    def add_source(

        self,

        source: ResearchSource

    ) -> None:

        self._sources[source.source_id] = source

    def get_source(

        self,

        source_id: str

    ) -> ResearchSource | None:

        return self._sources.get(

            source_id

        )
    
    def get_summary(self) -> dict:

        return {

            "source_count": len(self._sources)

        }