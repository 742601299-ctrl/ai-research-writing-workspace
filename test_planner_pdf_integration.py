import os

from dotenv import load_dotenv

from openai import OpenAI

from app.services.research_planner import ResearchPlanner

from app.services.research_source_factory import ResearchSourceFactory

from app.services.evidence_extractor import EvidenceExtractor

from app.tools.pdf_loader import PDFLoader

load_dotenv()

# 1. Create dependencies

client = OpenAI(

    api_key=os.getenv("OPENAI_API_KEY")

)

model = os.getenv("OPENAI_MODEL")

planner = ResearchPlanner(

    client=client,

    model=model

)

pdf_loader = PDFLoader()

source_factory = ResearchSourceFactory()

evidence_extractor = EvidenceExtractor(

    client=client,

    model=model

)

# 2. User provides a research topic

topic = (

    "Machine learning applications in "

    "pharmaceutical cold chain logistics"

)

# 3. Planner creates the research plan

research_plan = planner.create_plan(topic)

print("=== Research Plan ===")

print(f"Topic: {research_plan.topic}")

print(f"Objective: {research_plan.objective}")

print("\nResearch Questions:")

for index, research_question in enumerate(

    research_plan.research_questions,

    start=1

):

    print(

        f"{index}. {research_question.question}"

    )

# 4. User provides a PDF

pdf_path = "test_files/sample.pdf"

document = pdf_loader.load(pdf_path)

pdf_source = source_factory.from_document(document)

print("\n=== PDF ResearchSource ===")

print(f"Source Type: {pdf_source.source_type}")

print(f"Title: {pdf_source.title}")

print(f"Locator: {pdf_source.locator}")

# 5. Evaluate the PDF against every planner question

all_evidences = []

for research_question in research_plan.research_questions:

    evidences = evidence_extractor.extract(

        research_question=research_question.question,

        sources=[pdf_source]

    )

    all_evidences.extend(evidences)

# 6. Display the results

print("\n=== PDF Evidence Results ===")

for index, evidence in enumerate(

    all_evidences,

    start=1

):

    print(f"\nEvidence {index}")

    print(

        f"Research Question: "

        f"{evidence.research_question}"

    )

    print(

        f"Source: "

        f"{evidence.source.title}"

    )

    print(

        f"Relevance: "

        f"{evidence.relevance}"

    )

# 7. Validate the integration

assert len(

    research_plan.research_questions

) == 5

assert len(all_evidences) == 5

for research_question, evidence in zip(

    research_plan.research_questions,

    all_evidences

):

    assert (

        evidence.research_question

        == research_question.question

    )

    assert evidence.source == pdf_source

    assert (

        0.0

        <= evidence.relevance

        <= 1.0

    )

print(

    "\nAll Planner + PDF "

    "integration tests passed."

)