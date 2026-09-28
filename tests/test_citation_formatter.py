from app.models.research_source import ResearchSource

from app.models.research_state import (

    Finding,

    GapResearchQuestion,

    ResearchGap,

    ResearchState,

)

from app.models.traceable_evidence import TraceableEvidence

from app.services.citation_formatter import CitationFormatter

from app.services.citation_resolver import CitationResolver

from app.services.in_memory_vector_store import InMemoryVectorStore

from app.services.research_workspace import ResearchWorkspace

print("\n=== Citation Formatter Test ===\n")

# ---------------------------------------------------------

# Build workspace

# ---------------------------------------------------------

vector_store = InMemoryVectorStore()

workspace = ResearchWorkspace(

    vector_store=vector_store

)

# ---------------------------------------------------------

# Create sources

# ---------------------------------------------------------

source_1 = ResearchSource(

    source_type="web",

    title=(

        "Real-Time Anomaly Detection "

        "in Cold Chain Transportation"

    ),

    locator="https://example.com/paper-1",

    abstract=(

        "IoT-based real-time anomaly detection "

        "for cold-chain transportation."

    ),

    content=(

        "Cold-chain transportation can be monitored "

        "using IoT sensors and real-time anomaly detection."

    ),

)

source_2 = ResearchSource(

    source_type="web",

    title=(

        "Machine Learning for Pharmaceutical Cold Chains"

    ),

    locator="https://example.com/paper-2",

    abstract=(

        "Machine-learning methods for pharmaceutical "

        "cold-chain monitoring."

    ),

    content=(

        "Machine-learning models can support anomaly "

        "detection in pharmaceutical cold-chain logistics."

    ),

)

source_3 = ResearchSource(

    source_type="web",

    title="Edge AI for Temperature Monitoring",

    locator="https://example.com/paper-3",

    abstract=(

        "Edge AI methods for low-latency "

        "temperature monitoring."

    ),

    content=(

        "Edge processing can reduce latency for "

        "temperature-monitoring and anomaly-detection systems."

    ),

)

# ---------------------------------------------------------

# Add sources to workspace

# ---------------------------------------------------------

workspace.add_source(source_1)

workspace.add_source(source_2)

workspace.add_source(source_3)

# ---------------------------------------------------------

# Create traceable evidence

# ---------------------------------------------------------

evidence_1 = TraceableEvidence(

    chunk_id="chunk-1",

    source_id=source_1.source_id,

)

evidence_2 = TraceableEvidence(

    chunk_id="chunk-2",

    source_id=source_2.source_id,

)

evidence_3 = TraceableEvidence(

    chunk_id="chunk-3",

    source_id=source_3.source_id,

)

# ---------------------------------------------------------

# Create findings

# ---------------------------------------------------------

finding_1 = Finding(

    claim=(

        "Cold-chain anomaly detection increasingly combines "

        "real-time monitoring with machine-learning methods."

    ),

    evidence_ids=[

        evidence_1.evidence_id,

        evidence_2.evidence_id,

    ],

)

finding_2 = Finding(

    claim=(

        "Edge processing can support low-latency anomaly "

        "detection during pharmaceutical transportation."

    ),

    evidence_ids=[

        evidence_2.evidence_id,

        evidence_3.evidence_id,

    ],

)

# ---------------------------------------------------------

# Create research gap

#

# finding_1 -> source 1 + source 2

# finding_2 -> source 2 + source 3

#

# Therefore:

#

# gap -> source 1 + source 2 + source 3

# ---------------------------------------------------------

gap = ResearchGap(

    description=(

        "Current approaches do not yet provide a "

        "well-validated framework that combines robust "

        "machine-learning detection with efficient edge "

        "deployment across pharmaceutical cold-chain "

        "environments."

    ),

    supporting_finding_ids=[

        finding_1.finding_id,

        finding_2.finding_id,

    ],

)

# ---------------------------------------------------------

# Create gap-derived research question

#

# question -> gap

#          -> finding 1 + finding 2

#          -> source 1 + source 2 + source 3

# ---------------------------------------------------------

question = GapResearchQuestion(

    question=(

        "Can an edge-deployable anomaly-detection framework "

        "maintain accurate and low-latency detection across "

        "heterogeneous pharmaceutical cold-chain environments?"

    ),

    gap_ids=[

        gap.gap_id

    ],

)

# ---------------------------------------------------------

# Build research state

# ---------------------------------------------------------

research_state = ResearchState(

    evidence=[

        evidence_1,

        evidence_2,

        evidence_3,

    ],

    findings=[

        finding_1,

        finding_2,

    ],

    gaps=[

        gap

    ],

    gap_research_questions=[

        question

    ],

)

# ---------------------------------------------------------

# Build citation resolver

# ---------------------------------------------------------

citation_resolver = CitationResolver(

    workspace=workspace,

    research_state=research_state,

)

# ---------------------------------------------------------

# Build citation formatter

# ---------------------------------------------------------

citation_formatter = CitationFormatter(

    citation_resolver=citation_resolver,

    research_state=research_state,

)

# ---------------------------------------------------------

# Generate citation context

# ---------------------------------------------------------

context = citation_formatter.build_context()

print(context)

# ---------------------------------------------------------

# Test section existence

# ---------------------------------------------------------

assert (

    "FINDINGS WITH CITATIONS"

    in context

)

assert (

    "RESEARCH GAPS WITH CITATIONS"

    in context

)

assert (

    "RESEARCH QUESTIONS WITH CITATIONS"

    in context

)

assert (

    "SOURCES"

    in context

)

# ---------------------------------------------------------

# Test finding citation propagation

#

# finding_1 -> [1][2]

# finding_2 -> [2][3]

# ---------------------------------------------------------

assert (

    "Citations: [1][2]"

    in context

)

assert (

    "Citations: [2][3]"

    in context

)

# ---------------------------------------------------------

# Test gap / question citation propagation

#

# gap -> [1][2][3]

# question -> [1][2][3]

#

# We expect this marker at least twice:

# once for the gap and once for the question.

# ---------------------------------------------------------

assert (

    context.count(

        "Citations: [1][2][3]"

    )

    >= 2

)

# ---------------------------------------------------------

# Test IDs are present

# ---------------------------------------------------------

assert (

    finding_1.finding_id

    in context

)

assert (

    finding_2.finding_id

    in context

)

assert (

    gap.gap_id

    in context

)

assert (

    question.question_id

    in context

)

# ---------------------------------------------------------

# Test supporting relationships are visible

# ---------------------------------------------------------

assert (

    "Supporting Finding IDs:"

    in context

)

assert (

    "Gap IDs:"

    in context

)

# ---------------------------------------------------------

# Test global source numbering

# ---------------------------------------------------------

assert (

    "[1] Real-Time Anomaly Detection "

    "in Cold Chain Transportation"

    in context

)

assert (

    "[2] Machine Learning for "

    "Pharmaceutical Cold Chains"

    in context

)

assert (

    "[3] Edge AI for Temperature Monitoring"

    in context

)

# ---------------------------------------------------------

# Test source list deduplication

#

# Each source should appear only once in SOURCES,

# even though citations propagate through findings,

# gaps, and questions.

# ---------------------------------------------------------

assert (

    context.count(

        "[1] Real-Time Anomaly Detection "

        "in Cold Chain Transportation"

    )

    == 1

)

assert (

    context.count(

        "[2] Machine Learning for "

        "Pharmaceutical Cold Chains"

    )

    == 1

)

assert (

    context.count(

        "[3] Edge AI for Temperature Monitoring"

    )

    == 1

)

# ---------------------------------------------------------

# Test locators

# ---------------------------------------------------------

assert (

    "https://example.com/paper-1"

    in context

)

assert (

    "https://example.com/paper-2"

    in context

)

assert (

    "https://example.com/paper-3"

    in context

)

print(

    "\nAll citation formatter tests passed."

)