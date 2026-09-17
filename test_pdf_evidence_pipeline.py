import os

from dotenv import load_dotenv

from openai import OpenAI

from app.tools.pdf_loader import PDFLoader

from app.services.research_source_factory import ResearchSourceFactory

from app.services.evidence_extractor import EvidenceExtractor

load_dotenv()

# 1. Create dependencies

client = OpenAI(

    api_key=os.getenv("OPENAI_API_KEY")

)

model = os.getenv("OPENAI_MODEL")

pdf_loader = PDFLoader()

source_factory = ResearchSourceFactory()

evidence_extractor = EvidenceExtractor(

    client=client,

    model=model

)

# 2. Load PDF

pdf_path = "test_files/sample.pdf"

document = pdf_loader.load(pdf_path)

# 3. Convert Document -> ResearchSource

source = source_factory.from_document(document)

print("=== PDF ResearchSource ===")

print(f"Source Type: {source.source_type}")

print(f"Title: {source.title}")

print(f"Locator: {source.locator}")

print(f"Abstract Length: {len(source.abstract)}")

# 4. Test a highly relevant research question

relevant_question = (

    "How can machine learning detect temperature "

    "outliers in pharmaceutical cold chain logistics?"

)

relevant_evidences = evidence_extractor.extract(

    research_question=relevant_question,

    sources=[source]

)

relevant_evidence = relevant_evidences[0]

print("\n=== Relevant Question ===")

print(

    f"Research Question: "

    f"{relevant_evidence.research_question}"

)

print(

    f"Source: "

    f"{relevant_evidence.source.title}"

)

print(

    f"Relevance: "

    f"{relevant_evidence.relevance}"

)

# 5. Test an unrelated research question

unrelated_question = (

    "How can AI agents improve software project management?"

)

unrelated_evidences = evidence_extractor.extract(

    research_question=unrelated_question,

    sources=[source]

)

unrelated_evidence = unrelated_evidences[0]

print("\n=== Unrelated Question ===")

print(

    f"Research Question: "

    f"{unrelated_evidence.research_question}"

)

print(

    f"Source: "

    f"{unrelated_evidence.source.title}"

)

print(

    f"Relevance: "

    f"{unrelated_evidence.relevance}"

)

# 6. Validate pipeline

assert source.source_type == "pdf"

assert source.abstract != ""

assert len(relevant_evidences) == 1

assert len(unrelated_evidences) == 1

assert relevant_evidence.source == source

assert unrelated_evidence.source == source

assert (

    relevant_evidence.research_question

    == relevant_question

)

assert (

    unrelated_evidence.research_question

    == unrelated_question

)

assert (

    relevant_evidence.relevance

    > unrelated_evidence.relevance

)

print("\nAll PDF Evidence Pipeline tests passed.")