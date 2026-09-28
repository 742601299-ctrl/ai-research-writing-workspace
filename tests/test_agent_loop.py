import json

import os

from dotenv import load_dotenv

from openai import OpenAI

from app.models.research_state import ResearchState

from app.prompts.research_agent import RESEARCH_AGENT_INSTRUCTIONS

from app.services.citation_formatter import CitationFormatter

from app.services.citation_resolver import CitationResolver

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

# =========================================================

# Configuration

# =========================================================

MODEL_NAME = "gpt-5-mini"

RESEARCH_QUERY = (

    "Investigate current anomaly-detection approaches in "

    "pharmaceutical cold-chain logistics, identify an "

    "evidence-grounded research gap, and formulate one or more "

    "research questions worth investigating."

)

MAX_ITERATIONS = 25

MAX_SEARCHES = 8

MAX_RETRIEVALS = 12

MAX_CONSECUTIVE_UPDATE_FAILURES = 2

# =========================================================

# Research Agent Runtime Instructions

# =========================================================

RUNTIME_INSTRUCTIONS = """

IMPORTANT EXECUTION RULES:

1. Evidence ID rules

- Findings may only use chunk_id values that were actually returned by

  retrieve_literature during this research session.

- Never use source_id values as supporting_chunk_ids.

- Research gaps may only use finding_id values that already exist in

  research_state.findings.

- Never use chunk_id or source_id values as supporting_finding_ids.

- Gap-derived research questions may only use gap_id values that already

  exist in research_state.gaps.

- Never invent identifiers such as "0", "1", "2", shortened IDs, or guessed

  UUIDs.

- Copy identifiers exactly as they appear in the latest tool observation.

2. State dependency rules

The semantic research state has a strict dependency order:

retrieved chunks

    -> findings

    -> research gaps

    -> gap-derived research questions

Respect this dependency order.

If findings are needed, create findings first and do not create dependent gaps

or questions in that same call.

After the findings update succeeds, inspect the returned research_state and

copy the real finding_id values exactly.

Only then create a research gap using those real finding_id values.

After the gap update succeeds, inspect the returned research_state and copy

the real gap_id exactly.

Only then create gap-derived research questions.

3. update_research_state rules

Before calling update_research_state, inspect the latest observation fields:

- retrieved_chunk_ids

- research_state.findings

- research_state.gaps

- research_state.recommended_next_state_action

Use only identifiers explicitly present there.

Do not infer an ID from a claim, source, chunk, array position, or previous

failed call.

A supporting_chunk_id must come from retrieved_chunk_ids.

A supporting_finding_id must come from

research_state.findings[*].finding_id.

A gap_id must come from research_state.gaps[*].gap_id.

4. Validation failure rules

If update_research_state fails:

- read the error carefully;

- inspect the current research_state;

- determine which identifier or dependency was invalid;

- do not repeat the same failed update unchanged;

- do not repeatedly retrieve the same source merely to retry an invalid state

  update.

A failed state update means the proposed state transition was invalid.

It does not automatically mean more literature must be retrieved.

If the latest observation says state updates are temporarily blocked, do not

call update_research_state again.

Continue with retrieval, synthesis, or the final answer.

5. Retrieval rules

Never call retrieve_literature with an empty query.

Use a short but meaningful query describing the evidence you need.

Use source_ids only when you intentionally want to restrict retrieval to those

sources.

Otherwise omit source_ids or use null.

Do not repeatedly retrieve the same query from the same sources unless the

previous retrieval failed or a clearly different evidence need exists.

6. Search discipline

Search only when evidence needed for the user's research goal is not already

available in the workspace.

Once useful sources exist, prefer retrieve_literature.

Once sufficient evidence has been retrieved, prefer synthesis and state

updates over additional searching.

Do not search merely to increase the number of sources.

7. Stopping discipline

The goal is not to maximize tool calls.

Stop when the available evidence is sufficient to:

- characterize the current approaches;

- establish useful evidence-backed findings;

- synthesize an evidence-grounded research gap;

- derive focused research questions; and

- answer the user's research request.

Do not attempt to eliminate every uncertainty before answering.

"""

AGENT_INSTRUCTIONS = (

    RESEARCH_AGENT_INSTRUCTIONS

    + "\n\n"

    + RUNTIME_INSTRUCTIONS

)

# =========================================================

# Final Citation-Aware Synthesis Instructions

# =========================================================

FINAL_SYNTHESIS_INSTRUCTIONS = """

You are the final research synthesis layer.

You are NOT performing additional research.

You must write the final answer using only the verified research state and

citation context supplied to you.

STRICT RULES:

1. Do not introduce factual claims that are not supported by the supplied

   findings.

2. Preserve citation markers exactly as supplied, such as [1], [2], or

   [1][2].

3. Never invent a citation number.

4. Never cite a source that is not present in the supplied SOURCES section.

5. Do not claim that a source proves something beyond what the supplied

   finding says.

6. Clearly distinguish:

   - current approaches,

   - practical limitations,

   - the evidence-grounded research gap,

   - research questions.

7. Research gaps must be based on the supplied research state.

8. Research questions must be based on the supplied gap-derived research

   questions.

9. Do not perform new web searches, literature retrieval, or state updates.

10. Include a SOURCES section at the end.

11. Use the source numbering already present in the citation context.

12. Do not create new source numbers.

13. If evidence is insufficient for a claim, omit the claim rather than

    guessing.

The purpose of this stage is to transform verified research state into a

clear, readable, citation-aware research answer without breaking evidence

traceability.

"""

# =========================================================

# Core Services

# =========================================================

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

# =========================================================

# Citation Pipeline

# =========================================================

citation_resolver = CitationResolver(

    research_state=research_state,

    workspace=workspace

)

citation_formatter = CitationFormatter(

    citation_resolver=citation_resolver,

    research_state=research_state

)

# =========================================================

# Runtime State

# =========================================================

research_progress = {

    "iteration_count": 0,

    "search_count": 0,

    "retrieval_count": 0

}

retrieved_chunk_ids = set()

consecutive_update_failures = 0

state_updates_blocked = False

# =========================================================

# Helper Functions

# =========================================================

def get_recommended_next_state_action():

    if state_updates_blocked:

        return (

            "Do not call update_research_state again in this run. "

            "Use the retrieved evidence directly for synthesis and "

            "produce the final answer when sufficient."

        )

    if not research_state.findings:

        if retrieved_chunk_ids:

            return (

                "Create findings only. Use supporting_chunk_ids copied "

                "exactly from retrieved_chunk_ids. Do not create gaps or "

                "questions in the same call."

            )

        return (

            "Retrieve relevant literature before creating findings."

        )

    if not research_state.gaps:

        return (

            "Create a research gap only. Use supporting_finding_ids "

            "copied exactly from "

            "research_state.findings[*].finding_id. Do not create gap "

            "research questions in the same call."

        )

    if not research_state.gap_research_questions:

        return (

            "Create gap-derived research questions only. Use gap_ids "

            "copied exactly from research_state.gaps[*].gap_id."

        )

    return (

        "The semantic state already contains findings, a gap, and "

        "research questions. Prefer producing the final answer unless "

        "a specific evidence gap still prevents answering the user's "

        "request."

    )

def build_research_state_snapshot():

    return {

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

                "description": gap.description,

                "supporting_finding_ids":

                    gap.supporting_finding_ids

            }

            for gap in research_state.gaps

        ],

        "gap_research_questions": [

            {

                "question_id": question.question_id,

                "question": question.question,

                "gap_ids": question.gap_ids

            }

            for question

            in research_state.gap_research_questions

        ],

        "dependency_rules": {

            "finding_support": (

                "A finding must reference an exact chunk_id from "

                "retrieved_chunk_ids."

            ),

            "gap_support": (

                "A research gap must reference exact finding_id values "

                "that already exist in findings."

            ),

            "question_support": (

                "A gap research question must reference exact gap_id "

                "values that already exist in gaps."

            ),

            "important": (

                "Never invent, shorten, transform, or guess IDs. "

                "Copy them exactly from this observation."

            )

        },

        "recommended_next_state_action":

            get_recommended_next_state_action()

    }

def build_common_context():

    return {

        "workspace": {

            **workspace.get_summary(),

            "message": (

                "Sources in the workspace are indexed and available "

                "through retrieve_literature. Workspace presence alone "

                "does not mean their contents have been examined."

            )

        },

        "research_progress": {

            **research_progress,

            "message": (

                "These counts describe actions already taken. They are "

                "not research goals. Prefer existing evidence over "

                "increasing search or retrieval counts."

            )

        },

        "retrieved_chunk_ids": sorted(

            retrieved_chunk_ids

        ),

        "research_state":

            build_research_state_snapshot(),

        "state_update_control": {

            "consecutive_update_failures":

                consecutive_update_failures,

            "updates_blocked":

                state_updates_blocked

        }

    }

def make_guard_observation(

    tool_name,

    error_message

):

    return json.dumps(

        {

            "success": False,

            "tool_name": tool_name,

            "data": None,

            "error": error_message,

            **build_common_context()

        },

        ensure_ascii=False

    )

def collect_retrieved_chunk_ids(value):

    if isinstance(value, dict):

        for key, nested_value in value.items():

            if (

                key == "chunk_id"

                and isinstance(nested_value, str)

            ):

                retrieved_chunk_ids.add(

                    nested_value

                )

            else:

                collect_retrieved_chunk_ids(

                    nested_value

                )

        return

    if isinstance(value, list):

        for nested_value in value:

            collect_retrieved_chunk_ids(

                nested_value

            )

def print_debug(execution_result):

    print(

        "Execution Success:",

        execution_result.success

    )

    print(

        "Execution Error:",

        execution_result.error

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

        "Retrieved Chunk IDs:",

        len(retrieved_chunk_ids)

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

    print(

        "Gap Research Questions:",

        len(

            research_state.gap_research_questions

        )

    )

    print(

        "Consecutive Update Failures:",

        consecutive_update_failures

    )

    print(

        "State Updates Blocked:",

        state_updates_blocked

    )

def build_final_synthesis_input(

    citation_context

):

    research_snapshot = {

        "gaps": [

            {

                "gap_id": gap.gap_id,

                "description": gap.description,

                "supporting_finding_ids":

                    gap.supporting_finding_ids

            }

            for gap in research_state.gaps

        ],

        "gap_research_questions": [

            {

                "question_id": question.question_id,

                "question": question.question,

                "gap_ids": question.gap_ids

            }

            for question

            in research_state.gap_research_questions

        ]

    }

    return (

        "ORIGINAL RESEARCH REQUEST:\n\n"

        f"{RESEARCH_QUERY}\n\n"

        "VERIFIED CITATION CONTEXT:\n\n"

        f"{citation_context}\n\n"

        "VERIFIED RESEARCH GAP AND QUESTIONS:\n\n"

        f"{json.dumps(research_snapshot, ensure_ascii=False, indent=2)}\n\n"

        "Write the final research answer using only the verified "

        "information above."

    )

def run_final_citation_synthesis():

    if not research_state.findings:

        print(

            "\nCitation-aware synthesis skipped: "

            "no validated findings exist."

        )

        return

    citation_context = (

        citation_formatter.build_context()

    )

    print(

        "\n=== Citation Context ==="

    )

    print(

        citation_context

    )

    synthesis_input = (

        build_final_synthesis_input(

            citation_context

        )

    )

    synthesis_response = client.responses.create(

        model=MODEL_NAME,

        instructions=FINAL_SYNTHESIS_INSTRUCTIONS,

        input=synthesis_input

    )

    print(

        "\n=== Final Citation-Aware Answer ==="

    )

    print(

        synthesis_response.output_text

    )

# =========================================================

# Initial Agent Decision

# =========================================================

print(

    "\n=== Round 1: LLM Decision ==="

)

response = client.responses.create(

    model=MODEL_NAME,

    instructions=AGENT_INSTRUCTIONS,

    input=RESEARCH_QUERY,

    tools=tool_registry.get_tools(),

    parallel_tool_calls=False

)

# =========================================================

# Agent Loop

# =========================================================

for iteration in range(MAX_ITERATIONS):

    research_progress[

        "iteration_count"

    ] = iteration + 1

    print(

        f"\n=== Agent Iteration "

        f"{iteration + 1} ==="

    )

    function_calls = [

        item

        for item in response.output

        if item.type == "function_call"

    ]

    # -----------------------------------------------------

    # Agent has finished research

    # -----------------------------------------------------

    if not function_calls:

        print(

            "\n=== Agent Research Answer ==="

        )

        print(

            response.output_text

        )

        run_final_citation_synthesis()

        break

    tool_outputs = []

    for item in function_calls:

        print(

            "Tool:",

            item.name

        )

        print(

            "Arguments:",

            item.arguments

        )

        # =================================================

        # Search Budget Guard

        # =================================================

        if (

            item.name == "search_web"

            and research_progress["search_count"]

            >= MAX_SEARCHES

        ):

            observation = (

                make_guard_observation(

                    item.name,

                    (

                        "Search budget exhausted. "

                        "Do not search again. "

                        "Use the sources already in the workspace, "

                        "retrieve relevant literature if necessary, "

                        "update the semantic research state if valid, "

                        "or produce the final answer."

                    )

                )

            )

            print(

                "Execution Success:",

                False

            )

            print(

                "Execution Error:",

                "Search budget exhausted"

            )

            tool_outputs.append(

                {

                    "type":

                        "function_call_output",

                    "call_id":

                        item.call_id,

                    "output":

                        observation

                }

            )

            continue

        # =================================================

        # Retrieval Budget Guard

        # =================================================

        if (

            item.name == "retrieve_literature"

            and research_progress["retrieval_count"]

            >= MAX_RETRIEVALS

        ):

            observation = (

                make_guard_observation(

                    item.name,

                    (

                        "Retrieval budget exhausted. "

                        "Do not retrieve again. "

                        "Synthesize the evidence already retrieved, "

                        "update the semantic research state if valid, "

                        "or produce the final answer."

                    )

                )

            )

            print(

                "Execution Success:",

                False

            )

            print(

                "Execution Error:",

                "Retrieval budget exhausted"

            )

            tool_outputs.append(

                {

                    "type":

                        "function_call_output",

                    "call_id":

                        item.call_id,

                    "output":

                        observation

                }

            )

            continue

        # =================================================

        # State Update Failure Guard

        # =================================================

        if (

            item.name == "update_research_state"

            and state_updates_blocked

        ):

            observation = (

                make_guard_observation(

                    item.name,

                    (

                        "State updates are blocked for the remainder "

                        "of this run because repeated "

                        "update_research_state validation failures "

                        "occurred. Do not call "

                        "update_research_state again. Use the "

                        "retrieved evidence directly and produce the "

                        "final answer when sufficient."

                    )

                )

            )

            print(

                "Execution Success:",

                False

            )

            print(

                "Execution Error:",

                "State updates temporarily blocked"

            )

            tool_outputs.append(

                {

                    "type":

                        "function_call_output",

                    "call_id":

                        item.call_id,

                    "output":

                        observation

                }

            )

            continue

        # =================================================

        # Parse Tool Arguments

        # =================================================

        try:

            arguments = json.loads(

                item.arguments

            )

        except json.JSONDecodeError as error:

            observation = (

                make_guard_observation(

                    item.name,

                    (

                        "Invalid JSON arguments: "

                        f"{error}"

                    )

                )

            )

            print(

                "Execution Success:",

                False

            )

            print(

                "Execution Error:",

                f"Invalid JSON arguments: {error}"

            )

            tool_outputs.append(

                {

                    "type":

                        "function_call_output",

                    "call_id":

                        item.call_id,

                    "output":

                        observation

                }

            )

            continue

        # =================================================

        # Empty Retrieval Query Guard

        # =================================================

        if item.name == "retrieve_literature":

            query = arguments.get(

                "query"

            )

            if (

                not isinstance(query, str)

                or not query.strip()

            ):

                observation = (

                    make_guard_observation(

                        item.name,

                        (

                            "retrieve_literature requires a "

                            "non-empty query. Choose a short "

                            "meaningful query describing the "

                            "evidence needed and try again."

                        )

                    )

                )

                print(

                    "Execution Success:",

                    False

                )

                print(

                    "Execution Error:",

                    "Empty retrieval query blocked"

                )

                tool_outputs.append(

                    {

                        "type":

                            "function_call_output",

                        "call_id":

                            item.call_id,

                        "output":

                            observation

                    }

                )

                continue

            arguments["query"] = (

                query.strip()

            )

        # =================================================

        # Execute Tool

        # =================================================

        execution_result = (

            tool_executor.execute(

                tool_name=item.name,

                arguments=arguments

            )

        )

        # =================================================

        # Update Progress Counters

        # =================================================

        if execution_result.success:

            if item.name == "search_web":

                research_progress[

                    "search_count"

                ] += 1

            elif (

                item.name

                == "retrieve_literature"

            ):

                research_progress[

                    "retrieval_count"

                ] += 1

        # =================================================

        # Parse Tool Observation

        # =================================================

        observation_data = json.loads(

            execution_result.to_observation()

        )

        # =================================================

        # Record Retrieved Chunk IDs

        # =================================================

        if (

            item.name

            == "retrieve_literature"

            and execution_result.success

        ):

            collect_retrieved_chunk_ids(

                observation_data.get(

                    "data"

                )

            )

        # =================================================

        # Track State Update Failures

        # =================================================

        if (

            item.name

            == "update_research_state"

        ):

            if execution_result.success:

                consecutive_update_failures = 0

            else:

                consecutive_update_failures += 1

                if (

                    consecutive_update_failures

                    >=

                    MAX_CONSECUTIVE_UPDATE_FAILURES

                ):

                    state_updates_blocked = True

        # =================================================

        # Attach Runtime Context

        # =================================================

        observation_data.update(

            build_common_context()

        )

        if (

            item.name

            == "update_research_state"

            and not execution_result.success

        ):

            observation_data[

                "recovery_instruction"

            ] = (

                "Do not repeat the same failed state update. "

                "Use only exact IDs shown in "

                "retrieved_chunk_ids, "

                "research_state.findings, and "

                "research_state.gaps. "

                "If state updates are blocked, continue "

                "research or answer directly without another "

                "state update."

            )

        observation = json.dumps(

            observation_data,

            ensure_ascii=False

        )

        # =================================================

        # Debug Output

        # =================================================

        print_debug(

            execution_result

        )

        tool_outputs.append(

            {

                "type":

                    "function_call_output",

                "call_id":

                    item.call_id,

                "output":

                    observation

            }

        )

    # =====================================================

    # Continue Agent Reasoning

    # =====================================================

    response = client.responses.create(

        model=MODEL_NAME,

        instructions=AGENT_INSTRUCTIONS,

        previous_response_id=response.id,

        input=tool_outputs,

        tools=tool_registry.get_tools(),

        parallel_tool_calls=False

    )

# =========================================================

# Maximum Iteration Fallback

# =========================================================

else:

    print(

        "\nAgent stopped because "

        "max_iterations was reached."

    )

    if research_state.findings:

        run_final_citation_synthesis()