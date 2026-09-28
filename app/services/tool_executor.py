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

    GapResearchQuestion,

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

        # All chunks that have actually been returned by

        # retrieve_literature during this research session.

        #

        # key:

        #     chunk_id

        #

        # value:

        #     source_id

        self.retrieved_chunks: dict[str, str] = {}

        # Chunk IDs returned by the most recent

        # retrieve_literature call.

        #

        # This is useful for debugging and for exposing the

        # most recent retrieval result to the agent loop.

        self.last_retrieved_chunk_ids: list[str] = []

    def execute(

        self,

        tool_name: str,

        arguments: dict

    ) -> ToolExecutionResult:

        try:

            # =====================================================

            # search_web

            # =====================================================

            if tool_name == "search_web":

                args = SearchWebArgs(

                    **arguments

                )

                result = self.research_tools.search_web(

                    query=args.query,

                    max_results=args.max_results

                )

            # =====================================================

            # retrieve_literature

            # =====================================================

            elif tool_name == "retrieve_literature":

                args = RetrieveLiteratureArgs(

                    **arguments

                )

                result = self.research_tools.retrieve_literature(

                    query=args.query,

                    top_k=args.top_k,

                    source_ids=args.source_ids

                )

                # Reset the most recent retrieval list.

                self.last_retrieved_chunk_ids = []

                # Record every chunk that was actually returned

                # during this research session.

                for retrieval_result in result:

                    self.retrieved_chunks[

                        retrieval_result.chunk_id

                    ] = retrieval_result.source_id

                    self.last_retrieved_chunk_ids.append(

                        retrieval_result.chunk_id

                    )

            # =====================================================

            # get_source

            # =====================================================

            elif tool_name == "get_source":

                args = GetSourceArgs(

                    **arguments

                )

                result = self.research_tools.get_source(

                    source_id=args.source_id

                )

            # =====================================================

            # update_research_state

            # =====================================================

            elif tool_name == "update_research_state":

                args = UpdateResearchStateArgs(

                    **arguments

                )

                # -------------------------------------------------

                # Phase 0:

                # Enforce semantic-state dependency order

                # -------------------------------------------------

                #

                # Correct order:

                #

                # retrieved chunks

                #     ->

                # findings

                #     ->

                # research gaps

                #     ->

                # gap research questions

                #

                # IDs are generated when objects are committed.

                # Therefore dependent objects must not be created

                # in the same call.

                # -------------------------------------------------

                if (

                    args.new_findings

                    and (

                        args.new_gaps

                        or args.new_gap_research_questions

                    )

                ):

                    return ToolExecutionResult(

                        success=False,

                        tool_name=tool_name,

                        error=(

                            "Create findings in a separate "

                            "update_research_state call before creating "

                            "gaps or gap-derived research questions."

                        )

                    )

                if (

                    args.new_gaps

                    and args.new_gap_research_questions

                ):

                    return ToolExecutionResult(

                        success=False,

                        tool_name=tool_name,

                        error=(

                            "Create research gaps in a separate "

                            "update_research_state call before creating "

                            "gap-derived research questions."

                        )

                    )

                # -------------------------------------------------

                # Phase 1:

                # Collect currently valid IDs

                # -------------------------------------------------

                existing_finding_ids = {

                    finding.finding_id

                    for finding in self.research_state.findings

                }

                existing_gap_ids = {

                    gap.gap_id

                    for gap in self.research_state.gaps

                }

                existing_evidence_chunk_ids = {

                    evidence.chunk_id

                    for evidence in self.research_state.evidence

                }

                # -------------------------------------------------

                # Phase 2:

                # Validate new findings

                # -------------------------------------------------

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

                    for chunk_id in (

                        new_finding.supporting_chunk_ids

                    ):

                        # A chunk is valid only if:

                        #

                        # 1. it was actually returned by

                        #    retrieve_literature during this session;

                        #

                        # OR

                        #

                        # 2. it already exists in the semantic

                        #    evidence state.

                        if (

                            chunk_id not in self.retrieved_chunks

                            and

                            chunk_id

                            not in existing_evidence_chunk_ids

                        ):

                            return ToolExecutionResult(

                                success=False,

                                tool_name=tool_name,

                                error=(

                                    "Supporting chunk was not retrieved "

                                    "during this research session and "

                                    "does not exist in the current "

                                    "research evidence state: "

                                    f"{chunk_id}"

                                )

                            )

                # -------------------------------------------------

                # Phase 3:

                # Validate new research gaps

                # -------------------------------------------------

                for new_gap in args.new_gaps:

                    if not new_gap.supporting_finding_ids:

                        return ToolExecutionResult(

                            success=False,

                            tool_name=tool_name,

                            error=(

                                "A research gap must have at least one "

                                "supporting finding."

                            )

                        )

                    for finding_id in (

                        new_gap.supporting_finding_ids

                    ):

                        if finding_id not in existing_finding_ids:

                            return ToolExecutionResult(

                                success=False,

                                tool_name=tool_name,

                                error=(

                                    "Supporting finding does not exist "

                                    "in the current research state: "

                                    f"{finding_id}"

                                )

                            )

                # -------------------------------------------------

                # Phase 4:

                # Validate new gap-derived research questions

                # -------------------------------------------------

                for new_question in (

                    args.new_gap_research_questions

                ):

                    if not new_question.gap_ids:

                        return ToolExecutionResult(

                            success=False,

                            tool_name=tool_name,

                            error=(

                                "A gap research question must reference "

                                "at least one research gap."

                            )

                        )

                    for gap_id in new_question.gap_ids:

                        if gap_id not in existing_gap_ids:

                            return ToolExecutionResult(

                                success=False,

                                tool_name=tool_name,

                                error=(

                                    "Referenced research gap does not "

                                    "exist in the current research "

                                    "state: "

                                    f"{gap_id}"

                                )

                            )

                # -------------------------------------------------

                # Phase 5:

                # Prepare new state objects

                #

                # Nothing is committed yet.

                # -------------------------------------------------

                new_evidence = []

                new_findings = []

                new_gaps = []

                new_gap_research_questions = []

                evidence_by_chunk_id = {

                    evidence.chunk_id: evidence

                    for evidence in self.research_state.evidence

                }

                # -------------------------------------------------

                # Build findings + traceable evidence

                # -------------------------------------------------

                for new_finding in args.new_findings:

                    evidence_ids = []

                    for chunk_id in (

                        new_finding.supporting_chunk_ids

                    ):

                        evidence = evidence_by_chunk_id.get(

                            chunk_id

                        )

                        if evidence is None:

                            source_id = self.retrieved_chunks.get(

                                chunk_id

                            )

                            # This should normally never happen because

                            # validation above already guarantees that

                            # a new evidence chunk was retrieved.

                            #

                            # Keep the guard here so that we never

                            # silently create evidence with a missing

                            # source relationship.

                            if source_id is None:

                                return ToolExecutionResult(

                                    success=False,

                                    tool_name=tool_name,

                                    error=(

                                        "Unable to determine source_id "

                                        "for supporting chunk: "

                                        f"{chunk_id}"

                                    )

                                )

                            evidence = TraceableEvidence(

                                chunk_id=chunk_id,

                                source_id=source_id

                            )

                            evidence_by_chunk_id[

                                chunk_id

                            ] = evidence

                            new_evidence.append(

                                evidence

                            )

                        evidence_ids.append(

                            evidence.evidence_id

                        )

                    finding = Finding(

                        claim=new_finding.claim,

                        evidence_ids=evidence_ids

                    )

                    new_findings.append(

                        finding

                    )

                # -------------------------------------------------

                # Build research gaps

                # -------------------------------------------------

                for new_gap in args.new_gaps:

                    gap = ResearchGap(

                        description=new_gap.description,

                        supporting_finding_ids=(

                            new_gap.supporting_finding_ids

                        )

                    )

                    new_gaps.append(

                        gap

                    )

                # -------------------------------------------------

                # Build gap-derived research questions

                # -------------------------------------------------

                for new_question in (

                    args.new_gap_research_questions

                ):

                    question = GapResearchQuestion(

                        question=new_question.question,

                        gap_ids=new_question.gap_ids

                    )

                    new_gap_research_questions.append(

                        question

                    )

                # -------------------------------------------------

                # Resolve gaps

                # -------------------------------------------------

                resolved_gap_ids = set(

                    args.resolved_gap_ids

                )

                remaining_gaps = [

                    gap

                    for gap in self.research_state.gaps

                    if gap.gap_id not in resolved_gap_ids

                ]

                # -------------------------------------------------

                # Phase 6:

                # Atomic-style commit

                #

                # State is modified only after all validation and

                # object construction have succeeded.

                # -------------------------------------------------

                self.research_state.evidence.extend(

                    new_evidence

                )

                self.research_state.findings.extend(

                    new_findings

                )

                self.research_state.gaps = (

                    remaining_gaps

                    + new_gaps

                )

                self.research_state.gap_research_questions.extend(

                    new_gap_research_questions

                )

                result = self.research_state

            # =====================================================

            # Unknown tool

            # =====================================================

            else:

                return ToolExecutionResult(

                    success=False,

                    tool_name=tool_name,

                    error=f"Unknown tool: {tool_name}"

                )

            # =====================================================

            # Successful execution

            # =====================================================

            return ToolExecutionResult(

                success=True,

                tool_name=tool_name,

                data=result

            )

        # =========================================================

        # Pydantic argument validation errors

        # =========================================================

        except ValidationError as error:

            return ToolExecutionResult(

                success=False,

                tool_name=tool_name,

                error=f"Invalid tool arguments: {error}"

            )

        # =========================================================

        # Unexpected execution errors

        # =========================================================

        except Exception as error:

            return ToolExecutionResult(

                success=False,

                tool_name=tool_name,

                error=f"Tool execution failed: {error}"

            )