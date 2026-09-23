import json

import os

from dotenv import load_dotenv

from openai import OpenAI

from app.services.embedding_service import EmbeddingService

from app.services.in_memory_vector_store import InMemoryVectorStore

from app.services.research_source_factory import ResearchSourceFactory

from app.services.research_workspace import ResearchWorkspace

from app.services.retriever import Retriever

from app.services.tool_executor import ToolExecutor

from app.services.tool_registry import ToolRegistry

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

tool_executor = ToolExecutor(

    research_tools=research_tools

)

tool_registry = ToolRegistry()

print("\n=== Step 1: LLM Tool Decision ===")

response = client.responses.create(

    model="gpt-5.6",

    instructions=(

        "You are a research agent. "

        "Use the available research tools when they are needed. "

        "The research workspace is currently empty."

    ),

    input=(

        "Research the main anomaly detection methods used "

        "in pharmaceutical cold chain logistics."

    ),

    tools=tool_registry.get_tools(),

    parallel_tool_calls=False

)

function_calls = [

    item

    for item in response.output

    if item.type == "function_call"

]

assert function_calls

print(

    "Function calls:",

    len(function_calls)

)

print("\n=== Step 2: Execute Tool Calls ===")

for item in function_calls:

    print("\nTool Name:", item.name)

    print("Call ID:", item.call_id)

    print("Raw Arguments:", item.arguments)

    arguments = json.loads(

        item.arguments

    )

    execution_result = tool_executor.execute(

        tool_name=item.name,

        arguments=arguments

    )

    print(

        "Execution Success:",

        execution_result.success

    )

    print(

        "Execution Error:",

        execution_result.error

    )

    assert execution_result.success is True

    assert execution_result.data is not None

print("\n=== Tool Execution Flow Check ===")

print("LLM tool decision -> PASS")

print("ToolExecutor dispatch -> PASS")

print("Real tool execution -> PASS")

print("Tool execution flow -> PASS")