import os

from dotenv import load_dotenv

from openai import OpenAI

from app.models.search import ResearchQuestionResult

from app.tools.web_search import WebSearchTool

from app.services.evidence_extractor import EvidenceExtractor

load_dotenv()

# 1. Define research question and search query

research_question = (

    "How can AI agents improve code quality in software development?"

)

search_query = (

    "AI agents improve code quality software development"

)

# 2. Search sources using Tavily

search_tool = WebSearchTool()

search_results = search_tool.search(

    query=search_query,

    max_results=3

)

# 3. Build ResearchQuestionResult

question_result = ResearchQuestionResult(

    research_question=research_question,

    search_query=search_query,

    search_results=search_results

)

# 4. Create EvidenceExtractor

client = OpenAI(

    api_key=os.getenv("OPENAI_API_KEY")

)

evidence_extractor = EvidenceExtractor(

    client=client,

    model="gpt-5-mini"

)

# 5. Extract evidence

evidences = evidence_extractor.extract(

    question_result

)

# 6. Print results

print("=== Evidence Extraction Test ===")

print(

    f"\nResearch Question: "

    f"{research_question}"

)

for index, evidence in enumerate(

    evidences,

    start=1

):

    print(f"\nEvidence {index}")

    print(

        f"Title: "

        f"{evidence.title}"

    )

    print(

        f"URL: "

        f"{evidence.url}"

    )

    print(

        f"Abstract: "

        f"{evidence.abstract}"

    )

    print(

        f"Relevance: "

        f"{evidence.relevance}"

    )

    print("-" * 80)

print(

    f"\nTotal search results: "

    f"{len(search_results)}"

)

print(

    f"Total evidences: "

    f"{len(evidences)}"

)