from app.models.evidence import Evidence

from app.services.evidence_store import EvidenceStore

store = EvidenceStore()

evidence_1 = Evidence(

    research_question="AI Agent 如何提高代码质量？",

    title="Source A",

    url="https://example.com/a",

    abstract="AI agents can assist with automated code review and bug detection.",

    relevance=0.9

)

evidence_2 = Evidence(

    research_question="AI Agent 如何提高代码质量？",

    title="Source B",

    url="https://example.com/b",

    abstract="AI coding tools may introduce maintainability risks and require human review.",

    relevance=0.7

)

evidence_3 = Evidence(

    research_question="AI Agent 如何帮助软件测试？",

    title="Source C",

    url="https://example.com/c",

    abstract="AI agents can automate test generation and improve testing efficiency.",

    relevance=0.85

)

store.add(evidence_1)

store.add(evidence_2)

store.add(evidence_3)

print("=== All Evidence ===")

for evidence in store.get_all():

    print(evidence.abstract)

print("\n=== Evidence for Code Quality ===")

results = store.get_by_question(

    "AI Agent 如何提高代码质量？"

)

for evidence in results:

    print(evidence.abstract)

print("\n=== High Relevance Evidence ===")

results = store.filter_by_relevance(0.8)

for evidence in results:

    print(

        evidence.relevance,

        evidence.abstract

    )