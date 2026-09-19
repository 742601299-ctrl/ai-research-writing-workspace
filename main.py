from dotenv import load_dotenv

from openai import OpenAI

import os

from app.services.research_planner import ResearchPlanner

from app.tools.web_search import WebSearchTool

from app.services.evidence_extractor import EvidenceExtractor

from app.services.evidence_store import EvidenceStore

from app.services.research_source_factory import ResearchSourceFactory

from app.tools.pdf_loader import PDFLoader

from app.tools.token_chunker import TokenChunker

from app.services.embedding_service import EmbeddingService

from app.services.in_memory_vector_store import InMemoryVectorStore

from app.services.retriever import Retriever

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

model = os.getenv("OPENAI_MODEL")

client = OpenAI(api_key=api_key)

planner = ResearchPlanner(

    client=client,

    model=model

)

search_tool = WebSearchTool()

research_source_factory = ResearchSourceFactory()

pdf_loader = PDFLoader()

evidence_extractor = EvidenceExtractor(

    client=client,

    model=model

)

chunker = TokenChunker(

    chunk_size=800,

    overlap=50

)

embedding_service = EmbeddingService(

    client=client

)

vector_store = InMemoryVectorStore()

topic = input("请输入你的研究主题：")

pdf_path = input(

    "请输入参考 PDF 路径（可留空）："

).strip()

try:

    # =========================================================

    # 1. Research Planning

    # =========================================================

    plan = planner.create_plan(topic)

    print("\n=== Research Plan ===")

    print("研究主题：", plan.topic)

    print("研究目标：", plan.objective)

    print("\n研究问题：")

    for i, item in enumerate(

        plan.research_questions,

        start=1

    ):

        print(f"\n{i}. {item.question}")

        for query in item.search_queries:

            print(f"   - {query}")

    # =========================================================

    # 2. PDF Loading

    # =========================================================

    pdf_source = None

    document = None

    if pdf_path:

        document = pdf_loader.load(

            pdf_path

        )

        pdf_source = (

            research_source_factory.from_document(

                document

            )

        )

        print("\n=== PDF ResearchSource ===")

        print(

            f"Title: "

            f"{pdf_source.title}"

        )

        print(

            f"Locator: "

            f"{pdf_source.locator}"

        )

        print(

            f"Abstract: "

            f"{pdf_source.abstract}"

        )

    # =========================================================

    # 3. Web Search

    # =========================================================

    print("\n=== Web Search Results ===")

    research_results = []

    all_sources = []

    for i, item in enumerate(

        plan.research_questions,

        start=1

    ):

        query = item.search_queries[0]

        print(f"\n研究问题 {i}: {item.question}")

        print(f"搜索词: {query}")

        results = search_tool.search(

            query=query,

            max_results=2

        )

        sources = [

            research_source_factory.from_search_result(result)

            for result in results

        ]

        # Save Web sources for V0.5 retrieval indexing

        all_sources.extend(

            sources

        )

        # Keep original V0.4 Evidence behavior

        if pdf_source:

            sources.append(

                pdf_source

            )

        research_results.append(

            {

                "research_question": item.question,

                "sources": sources

            }

        )

        for j, result in enumerate(

            results,

            start=1

        ):

            print(f"\n  {j}. {result.title}")

            print(f"     URL: {result.url}")

            print(f"     {result.content[:200]}...")

    # =========================================================

    # 4. V0.5 Retrieval Index

    # =========================================================

    if pdf_source:

        all_sources.append(

            pdf_source

        )

    print("\n=== V0.5 Retrieval ===")

    all_chunks = []

    for source in all_sources:

        if (

            pdf_source

            and source.source_id == pdf_source.source_id

        ):

            chunks = chunker.chunk(

                source=source,

                pages=document.pages

            )

        else:

            chunks = chunker.chunk(

                source=source

            )

        all_chunks.extend(

            chunks

        )

    # =========================================================

    # 5. Embedding + VectorStore

    # =========================================================

    if all_chunks:

        chunk_texts = [

            chunk.text

            for chunk in all_chunks

        ]

        chunk_vectors = embedding_service.embed(

            chunk_texts

        )

        vector_store.add(

            chunks=all_chunks,

            vectors=chunk_vectors

        )

        # =====================================================

        # 6. ResearchQuestion -> Retriever

        # =====================================================

        retriever = Retriever(

            embedding_service=embedding_service,

            vector_store=vector_store

        )

        for i, item in enumerate(

            plan.research_questions,

            start=1

        ):

            print(

                f"\nResearch Question {i}: "

                f"{item.question}"

            )

            retrieval_results = retriever.retrieve(

                query=item.question,

                top_k=3

            )

            for rank, result in enumerate(

                retrieval_results,

                start=1

            ):

                print(

                    f"  Rank {rank} | "

                    f"Similarity: "

                    f"{result.similarity:.4f} | "

                    f"Source ID: "

                    f"{result.chunk.source_id} | "

                    f"Pages: "

                    f"{result.chunk.page_start}-"

                    f"{result.chunk.page_end}"

                )

                print(

                    f"  "

                    f"{result.chunk.text[:300]}..."

                )

    # =========================================================

    # 7. Evidence Extraction

    # =========================================================

    print("\n=== Evidence Extraction ===")

    evidence_store = EvidenceStore()

    for research_result in research_results:

        evidences = evidence_extractor.extract(

            research_question=research_result["research_question"],

            sources=research_result["sources"]

        )

        evidence_store.add_all(evidences)

    # =========================================================

    # 8. Evidence Output

    # =========================================================

    for i, evidence in enumerate(

        evidence_store.get_all(),

        start=1

    ):

        print(f"\nEvidence {i}")

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

            f"Abstract: "

            f"{evidence.source.abstract}"

        )

        print(

            f"Relevance: "

            f"{evidence.relevance}"

        )

except Exception as e:

    print("生成研究计划失败：", e)