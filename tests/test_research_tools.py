import os

from dotenv import load_dotenv

from openai import OpenAI

from app.services.embedding_service import EmbeddingService

from app.services.in_memory_vector_store import InMemoryVectorStore

from app.services.research_source_factory import ResearchSourceFactory

from app.services.research_workspace import ResearchWorkspace

from app.services.retriever import Retriever

from app.tools.research_tools import ResearchTools

from app.tools.token_chunker import TokenChunker

from app.tools.web_search import WebSearchTool

load_dotenv()

client = OpenAI(

    api_key=os.getenv("OPENAI_API_KEY")

)

vector_store = InMemoryVectorStore()

workspace = ResearchWorkspace(

    vector_store=vector_store

)

embedding_service = EmbeddingService(

    client=client

)

retriever = Retriever(

    embedding_service=embedding_service,

    vector_store=workspace.vector_store

)

research_tools = ResearchTools(

    web_search_tool=WebSearchTool(),

    source_factory=ResearchSourceFactory(),

    chunker=TokenChunker(

        chunk_size=800,

        overlap=50

    ),

    embedding_service=embedding_service,

    workspace=workspace,

    retriever=retriever

)

results = research_tools.search_web(

    query="pharmaceutical cold chain anomaly detection",

    max_results=2

)

print("\n=== Search Tool Results ===")

for result in results:

    print("\nSource ID:", result.source_id)

    print("Title:", result.title)

    print("Type:", result.source_type)

    print("Locator:", result.locator)

    print("Abstract:", result.abstract[:300])

    stored_source = workspace.get_source(

        result.source_id

    )

    print(

        "Stored in Workspace:",

        stored_source is not None

    )

print("\nTotal Search Results:", len(results))

retrieval_results = research_tools.retrieve_literature(

    query="What methods are used to detect anomalies in cold chain logistics?",

    top_k=3

)

print("\n=== Retrieval Tool Results ===")

for result in retrieval_results:

    print("\nSimilarity:", result.similarity)

    print("Source ID:", result.source_id)

    print("Pages:", result.page_start, "-", result.page_end)

    print("Text:", result.text[:500])

print("\n=== Get Source Tool Result ===")

if results:

    source_detail = research_tools.get_source(

        results[0].source_id

    )

    if source_detail is not None:

        print("Source ID:", source_detail.source_id)

        print("Title:", source_detail.title)

        print("Type:", source_detail.source_type)

        print("Locator:", source_detail.locator)

        print("Abstract:", source_detail.abstract[:300])

missing_source = research_tools.get_source(

    "non-existent-source-id"

)

print(

    "\nMissing Source:",

    missing_source

)

print("\n=== V0.6 Final Integration Check ===")

assert results, (

    "search_web() should return at least one result"

)

assert retrieval_results, (

    "retrieve_literature() should return at least one result"

)

searched_source_ids = {

    result.source_id

    for result in results

}

retrieved_source_id = retrieval_results[0].source_id

assert retrieved_source_id in searched_source_ids, (

    "retrieved source should come from sources added by search_web()"

)

retrieved_source_detail = research_tools.get_source(

    retrieved_source_id

)

assert retrieved_source_detail is not None, (

    "get_source() should find the source returned by retrieval"

)

assert (

    retrieved_source_detail.source_id

    == retrieved_source_id

)

assert missing_source is None

print("search_web() -> PASS")

print("retrieve_literature() -> PASS")

print("get_source() -> PASS")

print(

    "V0.6 Agent Tool Layer integration -> PASS"

)