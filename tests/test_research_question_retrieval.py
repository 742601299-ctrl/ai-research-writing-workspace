from dotenv import load_dotenv

from openai import OpenAI

from app.services.research_planner import ResearchPlanner

from app.tools.pdf_loader import PDFLoader

from app.services.research_source_factory import ResearchSourceFactory

from app.tools.token_chunker import TokenChunker

from app.services.embedding_service import EmbeddingService

from app.services.in_memory_vector_store import InMemoryVectorStore

from app.services.retriever import Retriever

load_dotenv()

client = OpenAI()

# 1. Create services

planner = ResearchPlanner(

    client=client,

    model="gpt-4o-mini"

)

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

# 2. Load and index PDF

document = pdf_loader.load(

    "test_files/sample.pdf"

)

source = source_factory.from_document(

    document

)

chunks = chunker.chunk(

    source=source,

    pages=document.pages

)

chunk_texts = [

    chunk.text

    for chunk in chunks

]

chunk_vectors = embedding_service.embed(

    chunk_texts

)

vector_store.add(

    chunks=chunks,

    vectors=chunk_vectors

)

# 3. Create Retriever

retriever = Retriever(

    embedding_service=embedding_service,

    vector_store=vector_store

)

# 4. Create ResearchPlan

topic = (

    "Outlier detection in pharmaceutical "

    "cold chain logistics"

)

research_plan = planner.create_plan(

    topic

)

# 5. Retrieve relevant chunks for each ResearchQuestion

print("Topic:")

print(research_plan.topic)

print()

print("Objective:")

print(research_plan.objective)

print()

for question_number, rq in enumerate(

    research_plan.research_questions,

    start=1

):

    print("=" * 80)

    print(

        f"Research Question {question_number}:"

    )

    print(rq.question)

    print()

    print("Search Queries:")

    for search_query in rq.search_queries:

        print(

            "-",

            search_query

        )

    print()

    results = retriever.retrieve(

        query=rq.question,

        top_k=3,

        source_ids=[source.source_id]

    )

    print("Relevant Chunks:")

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