from app.models.citation import Citation

from app.models.research_state import ResearchState

from app.services.citation_resolver import CitationResolver

class CitationFormatter:

    def __init__(

        self,

        citation_resolver: CitationResolver,

        research_state: ResearchState

    ):

        self.citation_resolver = citation_resolver

        self.research_state = research_state

    def format_citation_marker(

        self,

        citations: list[Citation]

    ) -> str:

        return "".join(

            f"[{citation.citation_number}]"

            for citation in citations

        )

    def format_source(

        self,

        citation: Citation

    ) -> str:

        source_line = (

            f"[{citation.citation_number}] "

            f"{citation.title}"

        )

        if citation.locator:

            source_line += (

                f"\n{citation.locator}"

            )

        return source_line

    def _append_citations(

        self,

        lines: list[str],

        citations: list[Citation]

    ) -> None:

        marker = self.format_citation_marker(

            citations

        )

        if marker:

            lines.append(

                f"Citations: {marker}"

            )

        else:

            lines.append(

                "Citations: none"

            )

    def build_context(self) -> str:

        citation_maps = (

            self.citation_resolver.resolve_all()

        )

        finding_citations = citation_maps[

            "findings"

        ]

        gap_citations = citation_maps[

            "gaps"

        ]

        question_citations = citation_maps[

            "questions"

        ]

        lines = [

            "FINDINGS WITH CITATIONS",

            ""

        ]

        # -------------------------------------------------

        # Findings

        # -------------------------------------------------

        for finding in self.research_state.findings:

            citations = finding_citations.get(

                finding.finding_id,

                []

            )

            lines.append(

                f"Finding ID: {finding.finding_id}"

            )

            lines.append("Claim:")

            lines.append(

                finding.claim

            )

            self._append_citations(

                lines,

                citations

            )

            lines.append("")

        # -------------------------------------------------

        # Research gaps

        # -------------------------------------------------

        lines.extend(

            [

                "RESEARCH GAPS WITH CITATIONS",

                ""

            ]

        )

        for gap in self.research_state.gaps:

            citations = gap_citations.get(

                gap.gap_id,

                []

            )

            lines.append(

                f"Gap ID: {gap.gap_id}"

            )

            lines.append("Description:")

            lines.append(

                gap.description

            )

            if gap.supporting_finding_ids:

                lines.append(

                    "Supporting Finding IDs: "

                    + ", ".join(

                        gap.supporting_finding_ids

                    )

                )

            self._append_citations(

                lines,

                citations

            )

            lines.append("")

        # -------------------------------------------------

        # Research questions

        # -------------------------------------------------

        lines.extend(

            [

                "RESEARCH QUESTIONS WITH CITATIONS",

                ""

            ]

        )

        for question in (

            self.research_state.gap_research_questions

        ):

            citations = question_citations.get(

                question.question_id,

                []

            )

            lines.append(

                f"Question ID: {question.question_id}"

            )

            lines.append("Question:")

            lines.append(

                question.question

            )

            if question.gap_ids:

                lines.append(

                    "Gap IDs: "

                    + ", ".join(

                        question.gap_ids

                    )

                )

            self._append_citations(

                lines,

                citations

            )

            lines.append("")

        # -------------------------------------------------

        # Collect globally unique citations

        # -------------------------------------------------

        unique_citations = {}

        for citation_map in (

            finding_citations,

            gap_citations,

            question_citations

        ):

            for citations in citation_map.values():

                for citation in citations:

                    unique_citations[

                        citation.citation_number

                    ] = citation

        # -------------------------------------------------

        # Sources

        # -------------------------------------------------

        lines.append("SOURCES")

        lines.append("")

        for citation_number in sorted(

            unique_citations

        ):

            citation = unique_citations[

                citation_number

            ]

            lines.append(

                self.format_source(

                    citation

                )

            )

            lines.append("")

        return "\n".join(lines).strip()