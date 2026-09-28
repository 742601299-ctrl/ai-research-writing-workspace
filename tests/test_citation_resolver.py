from app.models.research_source import ResearchSource

from app.models.traceable_evidence import TraceableEvidence

from app.models.research_state import (

    Finding,

    ResearchState

)

from app.services.in_memory_vector_store import InMemoryVectorStore

from app.services.research_workspace import ResearchWorkspace

from app.services.citation_resolver import CitationResolver

# ---------------------------------------------------------

# Workspace

# ---------------------------------------------------------

vector_store = InMemoryVectorStore()

workspace = ResearchWorkspace(

    vector_store=vector_store

)

# ---------------------------------------------------------

# Sources

# ---------------------------------------------------------

source_1 = ResearchSource(

    source_type="web",

    title="Real-Time Anomaly Detection in Cold Chain Transportation",

    locator="https://example.com/paper-1",

    abstract="Research on real-time cold-chain anomaly detection.",

    content="Example source content."

)

source_2 = ResearchSource(

    source_type="web",

    title="Machine Learning for Pharmaceutical Cold Chains",

    locator="https://example.com/paper-2",

    abstract="Research on machine learning in pharmaceutical logistics.",

    content="Example source content."

)

source_3 = ResearchSource(

    source_type="web",

    title="Edge AI for Temperature Monitoring",

    locator="https://example.com/paper-3",

    abstract="Research on edge AI for temperature monitoring.",

    content="Example source content."

)

workspace.add_source(source_1)

workspace.add_source(source_2)

workspace.add_source(source_3)

# ---------------------------------------------------------

# Evidence

# ---------------------------------------------------------

evidence_1 = TraceableEvidence(

    chunk_id="chunk-1",

    source_id=source_1.source_id

)

evidence_2 = TraceableEvidence(

    chunk_id="chunk-2",

    source_id=source_2.source_id

)

evidence_3 = TraceableEvidence(

    chunk_id="chunk-3",

    source_id=source_2.source_id

)

evidence_4 = TraceableEvidence(

    chunk_id="chunk-4",

    source_id=source_3.source_id

)

# ---------------------------------------------------------

# Findings

# ---------------------------------------------------------

finding_1 = Finding(

    claim=(

        "Cold-chain anomaly detection increasingly combines "

        "real-time monitoring with machine-learning methods."

    ),

    evidence_ids=[

        evidence_1.evidence_id,

        evidence_2.evidence_id

    ]

)

finding_2 = Finding(

    claim=(

        "Edge processing can support low-latency anomaly "

        "detection during pharmaceutical transportation."

    ),

    evidence_ids=[

        evidence_3.evidence_id,

        evidence_4.evidence_id

    ]

)

# ---------------------------------------------------------

# Research state

# ---------------------------------------------------------

research_state = ResearchState(

    evidence=[

        evidence_1,

        evidence_2,

        evidence_3,

        evidence_4

    ],

    findings=[

        finding_1,

        finding_2

    ]

)

# ---------------------------------------------------------

# Citation resolver

# ---------------------------------------------------------

resolver = CitationResolver(

    workspace=workspace,

    research_state=research_state

)

# ---------------------------------------------------------

# Test single finding

# ---------------------------------------------------------

citations = resolver.resolve_finding(

    finding_1

)

assert len(citations) == 2

assert citations[0].citation_number == 1

assert citations[0].source_id == source_1.source_id

assert citations[0].title == source_1.title

assert citations[0].source_type == source_1.source_type

assert citations[0].locator == source_1.locator

assert citations[1].citation_number == 2

assert citations[1].source_id == source_2.source_id

# ---------------------------------------------------------

# Test global citation resolution

# ---------------------------------------------------------

citation_map = resolver.resolve_all_findings()

finding_1_citations = citation_map[

    finding_1.finding_id

]

finding_2_citations = citation_map[

    finding_2.finding_id

]

# Finding 1:

#

# source_1 -> [1]

# source_2 -> [2]

assert len(finding_1_citations) == 2

assert (

    finding_1_citations[0].citation_number

    == 1

)

assert (

    finding_1_citations[0].source_id

    == source_1.source_id

)

assert (

    finding_1_citations[1].citation_number

    == 2

)

assert (

    finding_1_citations[1].source_id

    == source_2.source_id

)

# Finding 2:

#

# source_2 -> [2]

# source_3 -> [3]

#

# source_2 must keep citation number 2.

assert len(finding_2_citations) == 2

assert (

    finding_2_citations[0].citation_number

    == 2

)

assert (

    finding_2_citations[0].source_id

    == source_2.source_id

)

assert (

    finding_2_citations[1].citation_number

    == 3

)

assert (

    finding_2_citations[1].source_id

    == source_3.source_id

)

# ---------------------------------------------------------

# Output

# ---------------------------------------------------------

print("\n=== Citation Resolver Test ===")

for finding in research_state.findings:

    print("\nFinding:")

    print(finding.claim)

    print("Citations:")

    for citation in citation_map[

        finding.finding_id

    ]:

        print(

            f"[{citation.citation_number}] "

            f"{citation.title}"

        )

        print(

            f"    source_id: "

            f"{citation.source_id}"

        )

        print(

            f"    locator: "

            f"{citation.locator}"

        )

print(

    "\nAll citation resolver tests passed."

)