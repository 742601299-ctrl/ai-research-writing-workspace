from app.models.search import ResearchQuestionResult

from app.models.evidence import Evidence, EvidenceRelevanceResult

from app.tools.abstract_extractor import AbstractExtractor

class EvidenceExtractor:

    def __init__(self, client, model: str):

        self.client = client

        self.model = model

        self.abstract_extractor = AbstractExtractor()

    def extract(

        self,

        question_result: ResearchQuestionResult

    ) -> list[Evidence]:

        evidences = []

        for search_result in question_result.search_results:

            abstract = self.abstract_extractor.extract(search_result)

            prompt = f"""

You are a research evidence relevance evaluator.

Research question:

{question_result.research_question}

Source title:

{search_result.title}

Source abstract:

{abstract}

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

                research_question=question_result.research_question,

                title=search_result.title,

                url=search_result.url,

                abstract=abstract,

                relevance=relevance_result.relevance

            )

            evidences.append(evidence)

        return evidences