from uuid import uuid4

import tiktoken

from app.models.document import DocumentPage

from app.models.research_source import ResearchSource

from app.models.research_chunk import ResearchChunk

class TokenChunker:

    def __init__(

        self,

        chunk_size: int = 800,

        overlap: int = 50

    ):

        if chunk_size <= 0:

            raise ValueError(

                "chunk_size must be greater than 0"

            )

        if overlap < 0 or overlap >= chunk_size:

            raise ValueError(

                "overlap must satisfy 0 <= overlap < chunk_size"

            )

        self.chunk_size = chunk_size

        self.overlap = overlap

        self.encoding = tiktoken.get_encoding(

            "cl100k_base"

        )

    def chunk(

        self,

        source: ResearchSource,

        pages: list[DocumentPage] | None = None

    ) -> list[ResearchChunk]:

        if pages is not None:

            return self._chunk_pages(

                source,

                pages

            )

        return self._chunk_content(

            source

        )

    def _chunk_content(

        self,

        source: ResearchSource

    ) -> list[ResearchChunk]:

        if not source.content.strip():

            return []

        tokens = self.encoding.encode(

            source.content

        )

        return self._create_chunks(

            source=source,

            tokens=tokens

        )

    def _chunk_pages(

        self,

        source: ResearchSource,

        pages: list[DocumentPage]

    ) -> list[ResearchChunk]:

        all_tokens = []

        token_pages = []

        for i, page in enumerate(pages):

            page_text = page.text

            if i < len(pages) - 1:

                page_text += "\n\n"

            page_tokens = self.encoding.encode(

                page_text

            )

            all_tokens.extend(

                page_tokens

            )

            token_pages.extend(

                [page.page_number] * len(page_tokens)

            )

        return self._create_chunks(

            source=source,

            tokens=all_tokens,

            token_pages=token_pages

        )

    def _create_chunks(

        self,

        source: ResearchSource,

        tokens: list[int],

        token_pages: list[int] | None = None

    ) -> list[ResearchChunk]:

        if not tokens:

            return []

        chunks = []

        step = (

            self.chunk_size

            - self.overlap

        )

        for start in range(

            0,

            len(tokens),

            step

        ):

            end = min(

                start + self.chunk_size,

                len(tokens)

            )

            chunk_tokens = tokens[

                start:end

            ]

            chunk_text = self.encoding.decode(

                chunk_tokens

            )

            page_start = None

            page_end = None

            if token_pages is not None:

                chunk_pages = token_pages[

                    start:end

                ]

                if chunk_pages:

                    page_start = chunk_pages[0]

                    page_end = chunk_pages[-1]

            chunk = ResearchChunk(

                chunk_id=str(uuid4()),

                source_id=source.source_id,

                text=chunk_text,

                page_start=page_start,

                page_end=page_end

            )

            chunks.append(chunk)

            if end == len(tokens):

                break

        return chunks