from dotenv import load_dotenv

from openai import OpenAI

import os

from app.services.research_planner import ResearchPlanner
from app.tools.web_search import WebSearchTool
from app.models.search import ResearchQuestionResult
from app.services.evidence_extractor import EvidenceExtractor
from app.services.evidence_store import EvidenceStore

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

model = os.getenv("OPENAI_MODEL")

client = OpenAI(api_key=api_key)

planner = ResearchPlanner(
    client=client,
    model=model

)

search_tool = WebSearchTool()

evidence_extractor = EvidenceExtractor(

    client=client,

    model=model

)

topic = input("请输入你的研究主题：")

try:
    plan = planner.create_plan(topic)
    print("\n=== Research Plan ===")
    print("研究主题：", plan.topic)
    print("研究目标：", plan.objective)
    print("\n研究问题：")

    for i, item in enumerate(plan.research_questions, start=1):
        print(f"\n{i}. {item.question}")

        for query in item.search_queries:
            print(f"   - {query}")

    print("\n=== Web Search Results ===")
    
    research_results = []

    for i, item in enumerate(plan.research_questions, start=1):

        query = item.search_queries[0]
        print(f"\n研究问题 {i}: {item.question}")
        print(f"搜索词: {query}")
        results = search_tool.search(
            query=query,
            max_results=2
        )

        question_result = ResearchQuestionResult(
            research_question=item.question,
            search_query=query,
            search_results=results
        )

        research_results.append(question_result)

        for j, result in enumerate(results, start=1):
            print(f"\n  {j}. {result.title}")
            print(f"     URL: {result.url}")
            print(f"     {result.content[:200]}...")
        
    print("\n=== Evidence Extraction ===")

    evidence_store = EvidenceStore()

    for question_result in research_results:

        evidences = evidence_extractor.extract(question_result)

        evidence_store.add_all(evidences)

    for i, evidence in enumerate(evidence_store.get_all(), start=1):

        print(f"\nEvidence {i}")

        print(f"Question: {evidence.research_question}")

        print(f"Title: {evidence.title}")

        print(f"URL: {evidence.url}")

        print(f"Abstract: {evidence.abstract}")

        print(f"Relevance: {evidence.relevance}")

except Exception as e:
    print("生成研究计划失败：", e)