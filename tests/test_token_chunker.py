import tiktoken

from app.tools.pdf_loader import PDFLoader

from app.services.research_source_factory import ResearchSourceFactory

from app.tools.token_chunker import TokenChunker

pdf_path = "test_files/sample.pdf"

# 1. PDF -> Document

loader = PDFLoader()

document = loader.load(pdf_path)

# 2. Document -> ResearchSource

factory = ResearchSourceFactory()

source = factory.from_document(document)

# 3. ResearchSource + pages -> ResearchChunks

chunker = TokenChunker(

    chunk_size=800,

    overlap=50

)

chunks = chunker.chunk(

    source,

    document.pages

)

# 4. Inspect results

encoding = tiktoken.get_encoding("cl100k_base")

print("Title:", source.title)

print("Source ID:", source.source_id)

print("PDF pages:", len(document.pages))

print("Total chunks:", len(chunks))

print()

for i, chunk in enumerate(chunks):

    token_count = len(

        encoding.encode(chunk.text)

    )

    print(

        f"Chunk {i + 1}: "

        f"tokens={token_count}, "

        f"pages={chunk.page_start}-{chunk.page_end}"

    )