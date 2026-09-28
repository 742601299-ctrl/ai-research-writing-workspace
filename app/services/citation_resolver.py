from app.models.citation import Citation

from app.models.research_state import (

    Finding,

    ResearchGap,

    GapResearchQuestion,

    ResearchState

)

from app.services.research_workspace import ResearchWorkspace

class CitationResolver:

    def __init__(

        self,

        workspace: ResearchWorkspace,

        research_state: ResearchState

    ):

        self.workspace = workspace

        self.research_state = research_state

    def _build_evidence_by_id(self):

        return {

            evidence.evidence_id: evidence

            for evidence in self.research_state.evidence

        }

    def _build_finding_by_id(self):

        return {

            finding.finding_id: finding

            for finding in self.research_state.findings

        }

    def _build_gap_by_id(self):

        return {

            gap.gap_id: gap

            for gap in self.research_state.gaps

        }

    def _source_ids_for_finding(

        self,

        finding: Finding

    ) -> list[str]:

        evidence_by_id = self._build_evidence_by_id()

        source_ids = []

        for evidence_id in finding.evidence_ids:

            evidence = evidence_by_id.get(

                evidence_id

            )

            if evidence is None:

                continue

            if evidence.source_id not in source_ids:

                source_ids.append(

                    evidence.source_id

                )

        return source_ids

    def _source_ids_for_gap(

        self,

        gap: ResearchGap

    ) -> list[str]:

        finding_by_id = self._build_finding_by_id()

        source_ids = []

        for finding_id in gap.supporting_finding_ids:

            finding = finding_by_id.get(

                finding_id

            )

            if finding is None:

                continue

            finding_source_ids = (

                self._source_ids_for_finding(

                    finding

                )

            )

            for source_id in finding_source_ids:

                if source_id not in source_ids:

                    source_ids.append(

                        source_id

                    )

        return source_ids

    def _source_ids_for_question(

        self,

        question: GapResearchQuestion

    ) -> list[str]:

        gap_by_id = self._build_gap_by_id()

        source_ids = []

        for gap_id in question.gap_ids:

            gap = gap_by_id.get(

                gap_id

            )

            if gap is None:

                continue

            gap_source_ids = (

                self._source_ids_for_gap(

                    gap

                )

            )

            for source_id in gap_source_ids:

                if source_id not in source_ids:

                    source_ids.append(

                        source_id

                    )

        return source_ids

    def _build_citations(

        self,

        source_ids: list[str],

        source_number_map: dict[str, int] | None = None

    ) -> list[Citation]:

        if source_number_map is None:

            source_number_map = {}

        citations = []

        next_citation_number = (

            max(

                source_number_map.values(),

                default=0

            )

            + 1

        )

        for source_id in source_ids:

            source = self.workspace.get_source(

                source_id

            )

            if source is None:

                continue

            if source_id not in source_number_map:

                source_number_map[

                    source_id

                ] = next_citation_number

                next_citation_number += 1

            citation = Citation(

                citation_number=(

                    source_number_map[

                        source_id

                    ]

                ),

                source_id=source.source_id,

                title=source.title,

                source_type=source.source_type,

                locator=source.locator

            )

            citations.append(

                citation

            )

        return citations

    def resolve_finding(

        self,

        finding: Finding

    ) -> list[Citation]:

        source_ids = (

            self._source_ids_for_finding(

                finding

            )

        )

        return self._build_citations(

            source_ids

        )

    def resolve_gap(

        self,

        gap: ResearchGap

    ) -> list[Citation]:

        source_ids = (

            self._source_ids_for_gap(

                gap

            )

        )

        return self._build_citations(

            source_ids

        )

    def resolve_research_question(

        self,

        question: GapResearchQuestion

    ) -> list[Citation]:

        source_ids = (

            self._source_ids_for_question(

                question

            )

        )

        return self._build_citations(

            source_ids

        )

    def resolve_all(self) -> dict:

        source_number_map = {}

        findings = {}

        gaps = {}

        questions = {}

        for finding in self.research_state.findings:

            source_ids = (

                self._source_ids_for_finding(

                    finding

                )

            )

            findings[

                finding.finding_id

            ] = self._build_citations(

                source_ids,

                source_number_map

            )

        for gap in self.research_state.gaps:

            source_ids = (

                self._source_ids_for_gap(

                    gap

                )

            )

            gaps[

                gap.gap_id

            ] = self._build_citations(

                source_ids,

                source_number_map

            )

        for question in (

            self.research_state.gap_research_questions

        ):

            source_ids = (

                self._source_ids_for_question(

                    question

                )

            )

            questions[

                question.question_id

            ] = self._build_citations(

                source_ids,

                source_number_map

            )

        return {

            "findings": findings,

            "gaps": gaps,

            "questions": questions

        }

    def resolve_all_findings(

        self

    ) -> dict[str, list[Citation]]:

        return self.resolve_all()[

            "findings"

        ]