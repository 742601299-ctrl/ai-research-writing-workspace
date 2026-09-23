from pydantic import ValidationError

from app.models.tool_args import (

    SearchWebArgs,

    RetrieveLiteratureArgs,

    GetSourceArgs,

    UpdateResearchStateArgs

)

from app.models.tool_result import ToolExecutionResult

from app.models.research_state import (

    Finding,

    ResearchGap,

    ResearchState

)

from app.models.traceable_evidence import TraceableEvidence

from app.tools.research_tools import ResearchTools

class ToolExecutor:

    def __init__(

        self,

        research_tools: ResearchTools,

        research_state: ResearchState

    ):

        self.research_tools = research_tools

        self.research_state = research_state

        self.retrieved_chunks: dict[str, str] = {}

    def execute(

        self,

        tool_name: str,

        arguments: dict

    ) -> ToolExecutionResult:

        try:

            if tool_name == "search_web":

                args = SearchWebArgs(

                    **arguments

                )

                result = self.research_tools.search_web(

                    query=args.query,

                    max_results=args.max_results

                )

            elif tool_name == "retrieve_literature":

                args = RetrieveLiteratureArgs(

                    **arguments

                )

                result = self.research_tools.retrieve_literature(

                    query=args.query,

                    top_k=args.top_k,

                    source_ids=args.source_ids

                )

                for retrieval_result in result:

                    self.retrieved_chunks[

                        retrieval_result.chunk_id

                    ] = retrieval_result.source_id

            elif tool_name == "get_source":

                args = GetSourceArgs(

                    **arguments

                )

                result = self.research_tools.get_source(

                    source_id=args.source_id

                )

            elif tool_name == "update_research_state":

                args = UpdateResearchStateArgs(

                    **arguments

                )

                for new_finding in args.new_findings:

                    if not new_finding.supporting_chunk_ids:

                        return ToolExecutionResult(

                            success=False,

                            tool_name=tool_name,

                            error=(

                                "A finding must have at least one "

                                "supporting chunk."

                            )

                        )

                    for chunk_id in new_finding.supporting_chunk_ids:

                        if chunk_id not in self.retrieved_chunks:

                            return ToolExecutionResult(

                                success=False,

                                tool_name=tool_name,

                                error=(

                                    "Supporting chunk was not retrieved "

                                    "during this research session: "

                                    f"{chunk_id}"

                                )

                            )

                    evidence_ids = []

                    for chunk_id in new_finding.supporting_chunk_ids:

                        existing_evidence = next(

                            (

                                evidence

                                for evidence in self.research_state.evidence

                                if evidence.chunk_id == chunk_id

                            ),

                            None

                        )

                        if existing_evidence is not None:

                            evidence_ids.append(

                                existing_evidence.evidence_id

                            )

                            continue

                        evidence = TraceableEvidence(

                            chunk_id=chunk_id,

                            source_id=self.retrieved_chunks[

                                chunk_id

                            ]

                        )

                        self.research_state.evidence.append(

                            evidence

                        )

                        evidence_ids.append(

                            evidence.evidence_id

                        )

                    finding = Finding(

                        claim=new_finding.claim,

                        evidence_ids=evidence_ids

                    )

                    self.research_state.findings.append(

                        finding

                    )

                for description in args.new_gaps:

                    gap = ResearchGap(

                        description=description

                    )

                    self.research_state.gaps.append(

                        gap

                    )

                resolved_gap_ids = set(

                    args.resolved_gap_ids

                )

                self.research_state.gaps = [

                    gap

                    for gap in self.research_state.gaps

                    if gap.gap_id not in resolved_gap_ids

                ]

                result = self.research_state

            else:

                return ToolExecutionResult(

                    success=False,

                    tool_name=tool_name,

                    error=f"Unknown tool: {tool_name}"

                )

            return ToolExecutionResult(

                success=True,

                tool_name=tool_name,

                data=result

            )

        except ValidationError as error:

            return ToolExecutionResult(

                success=False,

                tool_name=tool_name,

                error=f"Invalid tool arguments: {error}"

            )

        except Exception as error:

            return ToolExecutionResult(

                success=False,

                tool_name=tool_name,

                error=f"Tool execution failed: {error}"

            )