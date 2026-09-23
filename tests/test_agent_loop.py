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

from app.prompts.research_agent import RESEARCH_AGENT_INSTRUCTIONS

from app.models.research_state import ResearchState

load_dotenv()

client = OpenAI(

    api_key=os.getenv("OPENAI_API_KEY")

)

vector_store = InMemoryVectorStore()

workspace = ResearchWorkspace(

    vector_store=vector_store

)

research_state = ResearchState()

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

    research_tools=research_tools,

    research_state=research_state

)

tool_registry = ToolRegistry()

print("\n=== Round 1: LLM Decision ===")

response = client.responses.create(

    model="gpt-4o-mini",

    instructions=RESEARCH_AGENT_INSTRUCTIONS,

    input=(

        "Research the main anomaly detection methods used "

        "in pharmaceutical cold chain logistics."

    ),

    tools=tool_registry.get_tools(),

    parallel_tool_calls=False

)

max_iterations = 12

research_progress = {

    "iteration_count": 0,

    "search_count": 0,

    "retrieval_count": 0

}

for iteration in range(max_iterations):

    research_progress["iteration_count"] = (

        iteration + 1

    )

    print(

        f"\n=== Agent Iteration {iteration + 1} ==="

    )

    function_calls = [

        item

        for item in response.output

        if item.type == "function_call"

    ]

    if not function_calls:

        print("\n=== Final Answer ===")

        print(response.output_text)

        break

    tool_outputs = []

    for item in function_calls:

        print("Tool:", item.name)

        print("Arguments:", item.arguments)

        try:

            arguments = json.loads(

                item.arguments

            )

        except json.JSONDecodeError as error:

            observation = json.dumps(

                {

                    "success": False,

                    "tool_name": item.name,

                    "data": None,

                    "error": (

                        "Invalid JSON arguments: "

                        f"{error}"

                    )

                }

            )

        else:

            execution_result = tool_executor.execute(

                tool_name=item.name,

                arguments=arguments

            )

            if execution_result.success:

                if item.name == "search_web":

                    research_progress["search_count"] += 1

                elif item.name == "retrieve_literature":

                    research_progress["retrieval_count"] += 1

            observation_data = json.loads(

                execution_result.to_observation()

            )

            observation_data["workspace"] = {

                **workspace.get_summary(),

                "message": (

                    "Sources in the workspace are indexed and available "

                    "through retrieve_literature."

                )

            }

            observation_data["research_progress"] = {

                **research_progress,

                "message": (

                    "These counts describe actions already taken. "

                    "Use them as context, not as fixed stopping rules. "

                    "Decide whether to search, retrieve, inspect a source, "

                    "or answer based on the actual research evidence."

                )

            }

            observation_data["research_state"] = {

                "evidence": [

                    {

                        "evidence_id": evidence.evidence_id,

                        "chunk_id": evidence.chunk_id,

                        "source_id": evidence.source_id

                    }

                    for evidence in research_state.evidence

                ],

                "findings": [

                    {

                        "finding_id": finding.finding_id,

                        "claim": finding.claim,

                        "evidence_ids": finding.evidence_ids

                    }

                    for finding in research_state.findings

                ],

                "gaps": [

                    {

                        "gap_id": gap.gap_id,

                        "description": gap.description

                    }

                    for gap in research_state.gaps

                ],

                "message": (

                    "This is the current semantic research state. "

                    "Each finding must be supported by traceable evidence. "

                    "Each evidence item points to a retrieved chunk and its source. "

                    "Gaps represent important missing information that materially "

                    "affects the user's research goal. "

                    "A remaining gap does not automatically require more searching."

                )

            }

            observation = json.dumps(

                observation_data,

                ensure_ascii=False

            )

            print(

                "Execution Success:",

                execution_result.success

            )

            print(

                "Workspace Sources:",

                workspace.get_summary()["source_count"]

            )

            print(

                "Research Progress:",

                research_progress

            )

            print(

                "Research Evidence:",

                len(research_state.evidence)

            )

            print(

                "Research Findings:",

                len(research_state.findings)

            )

            print(

                "Research Gaps:",

                len(research_state.gaps)

            )

        tool_outputs.append(

            {

                "type": "function_call_output",

                "call_id": item.call_id,

                "output": observation

            }

        )

    response = client.responses.create(

        model="gpt-5.6",

        previous_response_id=response.id,

        input=tool_outputs,

        tools=tool_registry.get_tools(),

        parallel_tool_calls=False

    )

else:

    print(

        "\nAgent stopped because "

        "max_iterations was reached."

    )