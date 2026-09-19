from dotenv import load_dotenv

from openai import OpenAI

from app.tools.pdf_loader import PDFLoader

from app.services.research_source_factory import ResearchSourceFactory

from app.tools.token_chunker import TokenChunker

from app.services.embedding_service import EmbeddingService

from app.services.in_memory_vector_store import InMemoryVectorStore

from app.services.retriever import Retriever

load_dotenv()

client = OpenAI()

# 1. Load PDF

pdf_path = "test_files/sample.pdf"

pdf_loader = PDFLoader()

document = pdf_loader.load(

    pdf_path

)

# 2. Convert Document -> ResearchSource

source_factory = ResearchSourceFactory()

source = source_factory.from_document(

    document

)

# 3. Split ResearchSource -> ResearchChunks

chunker = TokenChunker(

    chunk_size=800,

    overlap=50

)

chunks = chunker.chunk(

    source=source,

    pages=document.pages

)

# 4. Embed all chunks

embedding_service = EmbeddingService(

    client=client

)

chunk_texts = [

    chunk.text

    for chunk in chunks

]

chunk_vectors = embedding_service.embed(

    chunk_texts

)

# 5. Store chunks and vectors

vector_store = InMemoryVectorStore()

vector_store.add(

    chunks=chunks,

    vectors=chunk_vectors

)

# 6. Create Retriever

retriever = Retriever(

    embedding_service=embedding_service,

    vector_store=vector_store

)

# 7. Retrieve relevant PDF chunks

query = (

    "What methods are used to detect outliers "

    "in pharmaceutical cold chain logistics?"

)

results = retriever.retrieve(

    query=query,

    top_k=5,

    source_ids=[source.source_id]

)

# 8. Print results

print("PDF:")

print(source.title)

print()

print("Source ID:")

print(source.source_id)

print()

print("Total pages:")

print(len(document.pages))

print()

print("Total chunks:")

print(len(chunks))

print()

print("Query:")

print(query)

print()

for rank, result in enumerate(

    results,

    start=1

):

    print(

        f"Rank {rank}"

    )

    print(

        "Similarity:",

        result.similarity

    )

    print(

        "Pages:",

        f"{result.chunk.page_start}-{result.chunk.page_end}"

    )

    print("Text:")

    print(result.chunk.text)

    print()

    print("-" * 80)

    print()