from dotenv import load_dotenv

from openai import OpenAI

from app.models.research_source import ResearchSource

from app.tools.pdf_loader import PDFLoader

from app.services.research_source_factory import ResearchSourceFactory

from app.tools.token_chunker import TokenChunker

from app.services.embedding_service import EmbeddingService

from app.services.in_memory_vector_store import InMemoryVectorStore

from app.services.retriever import Retriever

load_dotenv()

client = OpenAI()

# 1. Create services

pdf_loader = PDFLoader()

source_factory = ResearchSourceFactory()

chunker = TokenChunker(

    chunk_size=800,

    overlap=50

)

embedding_service = EmbeddingService(

    client=client

)

vector_store = InMemoryVectorStore()

# 2. Create PDF source

document = pdf_loader.load(

    "test_files/sample.pdf"

)

pdf_source = source_factory.from_document(

    document

)

pdf_chunks = chunker.chunk(

    source=pdf_source,

    pages=document.pages

)

# 3. Create Web source

web_source = ResearchSource(

    source_type="web",

    title="Deep Learning for Medical Image Analysis",

    locator="https://example.com/deep-learning-medical-images",

    abstract=(

        "Deep learning methods are widely used "

        "for medical image classification."

    ),

    content=(

        "Deep learning techniques such as convolutional "

        "neural networks are widely used for medical image "

        "classification and disease detection. These models "

        "learn visual representations from medical images "

        "and can identify patterns associated with different "

        "diseases."

    )

)

web_chunks = chunker.chunk(

    source=web_source

)

# 4. Combine chunks from different sources

all_chunks = (

    pdf_chunks

    + web_chunks

)

chunk_texts = [

    chunk.text

    for chunk in all_chunks

]

# 5. Embed and index all sources together

vectors = embedding_service.embed(

    chunk_texts

)

vector_store.add(

    chunks=all_chunks,

    vectors=vectors

)

# 6. Create Retriever

retriever = Retriever(

    embedding_service=embedding_service,

    vector_store=vector_store

)

# 7. Search across ALL sources

query = (

    "How are temperature anomalies detected "

    "in pharmaceutical cold chain transportation?"

)

results = retriever.retrieve(

    query=query,

    top_k=5

)

print("PDF Source ID:")

print(pdf_source.source_id)

print()

print("Web Source ID:")

print(web_source.source_id)

print()

print("PDF chunks:")

print(len(pdf_chunks))

print("Web chunks:")

print(len(web_chunks))

print("Total chunks:")

print(len(all_chunks))

print()

print("Query:")

print(query)

print()

for rank, result in enumerate(

    results,

    start=1

):

    print(f"Rank {rank}")

    print(

        "Source ID:",

        result.chunk.source_id

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