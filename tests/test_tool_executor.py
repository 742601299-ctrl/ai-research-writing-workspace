import os

from dotenv import load_dotenv

from openai import OpenAI

from app.models.research_state import ResearchState

from app.services.embedding_service import EmbeddingService

from app.services.in_memory_vector_store import InMemoryVectorStore

from app.services.research_source_factory import ResearchSourceFactory

from app.services.research_workspace import ResearchWorkspace

from app.services.retriever import Retriever

from app.services.tool_executor import ToolExecutor

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

research_state = ResearchState()

tool_executor = ToolExecutor(

    research_tools=research_tools,

    research_state=research_state

)

print("\n=== Test 1: search_web ===")

search_result = tool_executor.execute(

    tool_name="search_web",

    arguments={

        "query": "pharmaceutical cold chain anomaly detection",

        "max_results": 2

    }

)

print("Success:", search_result.success)

print("Tool:", search_result.tool_name)

print("Error:", search_result.error)

assert search_result.success is True

assert search_result.data

print("\n=== Test 2: retrieve_literature ===")

retrieval_result = tool_executor.execute(

    tool_name="retrieve_literature",

    arguments={

        "query": "What anomaly detection methods are used?",

        "top_k": 3

    }

)

print("Success:", retrieval_result.success)

print("Tool:", retrieval_result.tool_name)

print("Error:", retrieval_result.error)

assert retrieval_result.success is True

assert retrieval_result.data

retrieved_chunk_id = retrieval_result.data[0].chunk_id

retrieved_source_id = retrieval_result.data[0].source_id

assert retrieved_chunk_id in tool_executor.retrieved_chunks

assert (

    tool_executor.retrieved_chunks[retrieved_chunk_id]

    == retrieved_source_id

)

print("\n=== Test 3: evidence-backed finding ===")

state_result = tool_executor.execute(

    tool_name="update_research_state",

    arguments={

        "new_findings": [

            {

                "claim": (

                    "Test finding grounded in retrieved literature."

                ),

                "supporting_chunk_ids": [

                    retrieved_chunk_id

                ]

            }

        ]

    }

)

print("Success:", state_result.success)

print("Tool:", state_result.tool_name)

print("Error:", state_result.error)

assert state_result.success is True

assert len(research_state.evidence) == 1

assert len(research_state.findings) == 1

evidence = research_state.evidence[0]

finding = research_state.findings[0]

assert evidence.chunk_id == retrieved_chunk_id

assert evidence.source_id == retrieved_source_id

assert finding.evidence_ids == [

    evidence.evidence_id

]

print("\n=== Test 4: unretrieved chunk rejection ===")

previous_evidence_count = len(

    research_state.evidence

)

previous_finding_count = len(

    research_state.findings

)

invalid_evidence_result = tool_executor.execute(

    tool_name="update_research_state",

    arguments={

        "new_findings": [

            {

                "claim": (

                    "This finding uses a chunk "

                    "the agent never retrieved."

                ),

                "supporting_chunk_ids": [

                    "fake-chunk-id"

                ]

            }

        ]

    }

)

print("Success:", invalid_evidence_result.success)

print("Tool:", invalid_evidence_result.tool_name)

print("Error:", invalid_evidence_result.error)

assert invalid_evidence_result.success is False

assert len(research_state.evidence) == (

    previous_evidence_count

)

assert len(research_state.findings) == (

    previous_finding_count

)

print("\n=== Test 5: get_source ===")

source_id = search_result.data[0].source_id

source_result = tool_executor.execute(

    tool_name="get_source",

    arguments={

        "source_id": source_id

    }

)

print("Success:", source_result.success)

print("Tool:", source_result.tool_name)

print("Error:", source_result.error)

assert source_result.success is True

assert source_result.data is not None

assert source_result.data.source_id == source_id

print("\n=== Test 6: invalid arguments ===")

invalid_result = tool_executor.execute(

    tool_name="retrieve_literature",

    arguments={

        "top_k": "invalid"

    }

)

print("Success:", invalid_result.success)

print("Tool:", invalid_result.tool_name)

print("Error:", invalid_result.error)

assert invalid_result.success is False

assert invalid_result.error is not None

print("\n=== Test 7: unknown tool ===")

unknown_result = tool_executor.execute(

    tool_name="unknown_tool",

    arguments={}

)

print("Success:", unknown_result.success)

print("Tool:", unknown_result.tool_name)

print("Error:", unknown_result.error)

assert unknown_result.success is False

assert unknown_result.error == (

    "Unknown tool: unknown_tool"

)

print("\n=== ToolExecutor Integration Check ===")

print("search_web dispatch -> PASS")

print("retrieve_literature dispatch -> PASS")

print("retrieved chunk registry -> PASS")

print("evidence-backed finding -> PASS")

print("unretrieved chunk rejection -> PASS")

print("get_source dispatch -> PASS")

print("argument validation -> PASS")

print("unknown tool handling -> PASS")

print("ToolExecutor -> PASS")