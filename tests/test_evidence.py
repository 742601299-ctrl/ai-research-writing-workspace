from app.models.research_source import ResearchSource

from app.models.evidence import Evidence

source = ResearchSource(

    source_type="web",

    title="Example Source",

    locator="https://example.com/article",

    abstract=(

        "AI agents can automate code review, detect potential defects, "

        "and generate test cases."

    ),

    content=(

        "AI agents can automate code review, detect potential defects, "

        "and generate test cases. These capabilities may help developers "

        "identify software quality issues earlier in the development process."

    )

)

evidence = Evidence(

    research_question=(

        "AI Agent 如何提升软件开发中的代码质量？"

    ),

    source=source,

    relevance=0.75

)

print("\n=== Evidence Model Test ===")

print(

    f"Question: "

    f"{evidence.research_question}"

)

print(

    f"Source Type: "

    f"{evidence.source.source_type}"

)

print(

    f"Title: "

    f"{evidence.source.title}"

)

print(

    f"Locator: "

    f"{evidence.source.locator}"

)

print(

    f"Relevance: "

    f"{evidence.relevance}"

)

assert evidence.research_question == (

    "AI Agent 如何提升软件开发中的代码质量？"

)

assert evidence.source == source

assert evidence.source.source_type == "web"

assert evidence.source.title == "Example Source"

assert evidence.source.locator == (

    "https://example.com/article"

)

assert evidence.relevance == 0.75

print("\nEvidence model test passed.")