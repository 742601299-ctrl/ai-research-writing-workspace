from app.models.research_source import ResearchSource

from app.models.evidence import Evidence

from app.services.evidence_store import EvidenceStore

store = EvidenceStore()

source_1 = ResearchSource(

    source_type="web",

    title="Source A",

    locator="https://example.com/a",

    abstract=(

        "AI agents can assist with automated "

        "code review and bug detection."

    ),

    content=(

        "AI agents can assist with automated "

        "code review and bug detection."

    )

)

source_2 = ResearchSource(

    source_type="web",

    title="Source B",

    locator="https://example.com/b",

    abstract=(

        "AI coding tools may introduce maintainability "

        "risks and require human review."

    ),

    content=(

        "AI coding tools may introduce maintainability "

        "risks and require human review."

    )

)

source_3 = ResearchSource(

    source_type="web",

    title="Source C",

    locator="https://example.com/c",

    abstract=(

        "AI agents can automate test generation "

        "and improve testing efficiency."

    ),

    content=(

        "AI agents can automate test generation "

        "and improve testing efficiency."

    )

)

evidence_1 = Evidence(

    research_question="AI Agent 如何提高代码质量？",

    source=source_1,

    relevance=0.9

)

evidence_2 = Evidence(

    research_question="AI Agent 如何提高代码质量？",

    source=source_2,

    relevance=0.7

)

evidence_3 = Evidence(

    research_question="AI Agent 如何帮助软件测试？",

    source=source_3,

    relevance=0.85

)

store.add(evidence_1)

store.add(evidence_2)

store.add(evidence_3)

print("=== All Evidence ===")

all_evidences = store.get_all()

for evidence in all_evidences:

    print(

        evidence.source.abstract

    )

assert len(all_evidences) == 3

print("\n=== Evidence for Code Quality ===")

results = store.get_by_question(

    "AI Agent 如何提高代码质量？"

)

for evidence in results:

    print(

        evidence.source.abstract

    )

assert len(results) == 2

assert all(

    evidence.research_question

    == "AI Agent 如何提高代码质量？"

    for evidence in results

)

print("\n=== High Relevance Evidence ===")

results = store.filter_by_relevance(0.8)

for evidence in results:

    print(

        evidence.relevance,

        evidence.source.abstract

    )

assert len(results) == 2

assert all(

    evidence.relevance >= 0.8

    for evidence in results

)

print("\nAll EvidenceStore tests passed.")