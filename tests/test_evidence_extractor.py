import os

from dotenv import load_dotenv

from openai import OpenAI

from app.models.research_source import ResearchSource

from app.services.evidence_extractor import EvidenceExtractor

load_dotenv()

# 1. Define research question

research_question = (

    "How can AI agents improve code quality in software development?"

)

# 2. Build ResearchSource objects directly

# We only test EvidenceExtractor here.

sources = [

    ResearchSource(

        source_type="web",

        title="AI Agents for Code Review",

        locator="https://example.com/code-review",

        abstract=(

            "AI agents can improve software code quality by automating "

            "code review, detecting bugs, and identifying potential "

            "security vulnerabilities."

        ),

        content=(

            "AI agents are increasingly used in automated code review "

            "and software quality assurance workflows."

        )

    ),

    ResearchSource(

        source_type="web",

        title="AI Agents for Project Scheduling",

        locator="https://example.com/project-scheduling",

        abstract=(

            "AI agents can assist project managers with task scheduling, "

            "resource allocation, and project progress monitoring."

        ),

        content=(

            "AI agents can support software project management by "

            "automating scheduling and resource planning."

        )

    )

]

# 3. Create EvidenceExtractor

client = OpenAI(

    api_key=os.getenv("OPENAI_API_KEY")

)

evidence_extractor = EvidenceExtractor(

    client=client,

    model="gpt-5-mini"

)

# 4. Evaluate evidence relevance

evidences = evidence_extractor.extract(

    research_question=research_question,

    sources=sources

)

# 5. Print results

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

        f"Abstract: "

        f"{evidence.source.abstract}"

    )

    print(

        f"Relevance: "

        f"{evidence.relevance}"

    )

    print("-" * 80)

# 6. Basic checks

assert len(evidences) == len(sources)

for evidence in evidences:

    assert evidence.research_question == research_question

    assert evidence.source in sources

    assert 0 <= evidence.relevance <= 1

print(

    f"\nTotal sources: "

    f"{len(sources)}"

)

print(

    f"Total evidences: "

    f"{len(evidences)}"

)

print("\nAll EvidenceExtractor tests passed.")