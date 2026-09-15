from app.models.evidence import Evidence

class EvidenceStore:

    def __init__(self):

        self.evidences: list[Evidence] = []

    def add(self, evidence: Evidence):

        self.evidences.append(evidence)

    def add_all(self, evidences: list[Evidence]):

        self.evidences.extend(evidences)

    def get_all(self) -> list[Evidence]:

        return self.evidences

    def get_by_question(self, research_question: str) -> list[Evidence]:

        return [

            evidence

            for evidence in self.evidences

            if evidence.research_question == research_question

        ]

    def filter_by_relevance(self, min_score: float) -> list[Evidence]:

        return [

            evidence

            for evidence in self.evidences

            if evidence.relevance >= min_score

        ]