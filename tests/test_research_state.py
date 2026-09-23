from app.models.research_state import (

    Finding,

    ResearchGap,

    ResearchState

)

print("\n=== ResearchState Check ===")

state = ResearchState()

assert state.findings == []

assert state.gaps == []

print("empty state -> PASS")

finding = Finding(

    claim=(

        "Threshold-based detection is commonly "

        "used in cold-chain monitoring."

    )

)

state.findings.append(finding)

assert len(state.findings) == 1

assert state.findings[0].claim == finding.claim

assert state.findings[0].finding_id

print("add finding -> PASS")

gap = ResearchGap(

    description=(

        "Evidence about pharmaceutical-specific "

        "machine learning deployment is limited."

    )

)

state.gaps.append(gap)

assert len(state.gaps) == 1

assert state.gaps[0].description == gap.description

assert state.gaps[0].gap_id

print("add gap -> PASS")

resolved_gap_id = gap.gap_id

state.gaps = [

    existing_gap

    for existing_gap in state.gaps

    if existing_gap.gap_id != resolved_gap_id

]

assert state.gaps == []

print("resolve gap by id -> PASS")

print("ResearchState -> PASS")