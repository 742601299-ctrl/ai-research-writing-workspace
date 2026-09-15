from dotenv import load_dotenv

from openai import OpenAI

from app.models.search import SearchResult, ResearchQuestionResult

from app.services.evidence_extractor import EvidenceExtractor

import os

load_dotenv()

client = OpenAI(

    api_key=os.getenv("OPENAI_API_KEY")

)

model = os.getenv("OPENAI_MODEL")

question_result = ResearchQuestionResult(

    research_question="AI Agent 如何提升软件开发中的代码质量？",

    search_query="AI agents improving code quality",

    search_results=[

        SearchResult(

            title="Example Source",

            url="https://example.com/article",

            snippet=(

                "AI agents can automate code review, detect potential defects, "

                "and generate test cases. These capabilities may help developers "

                "identify software quality issues earlier in the development process."

            )

        )

    ]

)

extractor = EvidenceExtractor(

    client=client,

    model=model

)

evidences = extractor.extract(question_result)

for i, evidence in enumerate(evidences, start=1):

    print(f"\nEvidence {i}")

    print(f"Question: {evidence.research_question}")

    print(f"Source: {evidence.source_title}")

    print(f"URL: {evidence.source_url}")

    print(f"Evidence: {evidence.evidence_text}")

    print(f"Relevance: {evidence.relevance_score}")