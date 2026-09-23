from app.models.tool_result import (

    SearchToolResult,

    RetrievalToolResult,

    SourceDetailResult

)

from app.services.retriever import Retriever

from app.services.embedding_service import EmbeddingService

from app.services.research_source_factory import ResearchSourceFactory

from app.services.research_workspace import ResearchWorkspace

from app.tools.token_chunker import TokenChunker

from app.tools.web_search import WebSearchTool

class ResearchTools:

    def __init__(

    self,

    web_search_tool: WebSearchTool,

    source_factory: ResearchSourceFactory,

    chunker: TokenChunker,

    embedding_service: EmbeddingService,

    workspace: ResearchWorkspace,

    retriever: Retriever

    ):

        self.web_search_tool = web_search_tool

        self.source_factory = source_factory

        self.chunker = chunker

        self.embedding_service = embedding_service

        self.workspace = workspace

        self.retriever = retriever

    def search_web(

        self,

        query: str,

        max_results: int = 5

    ) -> list[SearchToolResult]:

        search_results = self.web_search_tool.search(

            query=query,

            max_results=max_results

        )

        tool_results = []

        for search_result in search_results:

            source = self.source_factory.from_search_result(

                search_result

            )

            self.workspace.add_source(

                source

            )

            chunks = self.chunker.chunk(

                source

            )

            if chunks:

                vectors = self.embedding_service.embed(

                    [

                        chunk.text

                        for chunk in chunks

                    ]

                )

                self.workspace.vector_store.add(

                    chunks=chunks,

                    vectors=vectors

                )

            tool_results.append(

                SearchToolResult(

                    source_id=source.source_id,

                    title=source.title,

                    source_type=source.source_type,

                    locator=source.locator,

                    abstract=source.abstract

                )

            )

        return tool_results
    
    def retrieve_literature(

        self,

        query: str,

        top_k: int = 5,

        source_ids: list[str] | None = None

    ) -> list[RetrievalToolResult]:

        retrieval_results = self.retriever.retrieve(

            query=query,

            top_k=top_k,

            source_ids=source_ids

        )

        tool_results = []

        for result in retrieval_results:

            tool_results.append(

                RetrievalToolResult(

                    chunk_id=result.chunk.chunk_id,

                    source_id=result.chunk.source_id,

                    text=result.chunk.text,

                    page_start=result.chunk.page_start,

                    page_end=result.chunk.page_end,

                    similarity=result.similarity

                )

            )

        return tool_results
    
    def get_source(

        self,

        source_id: str

    ) -> SourceDetailResult | None:

        source = self.workspace.get_source(

            source_id

        )

        if source is None:

            return None

        return SourceDetailResult(

            source_id=source.source_id,

            source_type=source.source_type,

            title=source.title,

            locator=source.locator,

            abstract=source.abstract

        )