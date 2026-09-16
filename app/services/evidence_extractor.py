from app.models.research_source import ResearchSource

from app.models.evidence import Evidence, EvidenceRelevanceResult

class EvidenceExtractor:

    def __init__(self, client, model: str):

        self.client = client

        self.model = model

    def extract(

        self,

        research_question: str,

        sources: list[ResearchSource]

    ) -> list[Evidence]:

        evidences = []

        for source in sources:

            prompt = f"""

You are a research evidence relevance evaluator.

Research question:

{research_question}

Source title:

{source.title}

Source abstract:

{source.abstract}

Your task:

Evaluate how relevant the source abstract is to answering the research question.

Return a relevance score between 0 and 1.

Scoring guideline:

- 0.0: Completely irrelevant to the research question.

- 0.25: Only weakly related to the general topic.

- 0.5: Partially relevant and provides useful background.

- 0.75: Clearly relevant and helps answer the research question.

- 1.0: Directly and strongly addresses the research question.

Base the score only on the provided abstract.

Do not invent information.

"""

            response = self.client.responses.parse(

                model=self.model,

                input=[

                    {

                        "role": "user",

                        "content": prompt

                    }

                ],

                text_format=EvidenceRelevanceResult

            )

            relevance_result = response.output_parsed

            evidence = Evidence(

                research_question=research_question,

                source=source,

                relevance=relevance_result.relevance

            )

            evidences.append(evidence)

        return evidences