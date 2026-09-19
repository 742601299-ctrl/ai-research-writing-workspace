from dotenv import load_dotenv

from openai import OpenAI

from app.models.research_chunk import ResearchChunk

from app.services.embedding_service import EmbeddingService

from app.services.in_memory_vector_store import InMemoryVectorStore

load_dotenv()

client = OpenAI()

embedding_service = EmbeddingService(

    client=client

)

vector_store = InMemoryVectorStore()

chunks = [

    ResearchChunk(

        chunk_id="chunk-1",

        source_id="source-1",

        text="Machine learning can detect temperature anomalies in cold chain logistics."

    ),

    ResearchChunk(

        chunk_id="chunk-2",

        source_id="source-1",

        text="Temperature sensors are used to monitor pharmaceutical products during transportation."

    ),

    ResearchChunk(

        chunk_id="chunk-3",

        source_id="source-2",

        text="Cristiano Ronaldo is a professional football player."

    )

]

texts = [

    chunk.text

    for chunk in chunks

]

vectors = embedding_service.embed(

    texts

)

vector_store.add(

    chunks=chunks,

    vectors=vectors

)

query = (

    "How can AI detect abnormal temperature "

    "changes during transportation?"

)

query_vector = embedding_service.embed(

    [query]

)[0]

results = vector_store.search(

    query_vector=query_vector,

    top_k=3

)

print("Query:")

print(query)

print()

for rank, result in enumerate(

    results,

    start=1

):

    print(

        f"Rank {rank}:"

    )

    print(

        "Chunk ID:",

        result.chunk.chunk_id

    )

    print(

        "Source ID:",

        result.chunk.source_id

    )

    print(

        "Similarity:",

        result.similarity

    )

    print(

        "Text:",

        result.chunk.text

    )

    print()

print("Filtered results:")

print()

filtered_results = vector_store.search(

    query_vector=query_vector,

    top_k=3,

    source_ids=["source-2"]

)

for rank, result in enumerate(

    filtered_results,

    start=1

):

    print(

        f"Rank {rank}:"

    )

    print(

        "Chunk ID:",

        result.chunk.chunk_id

    )

    print(

        "Source ID:",

        result.chunk.source_id

    )

    print(

        "Similarity:",

        result.similarity

    )

    print(

        "Text:",

        result.chunk.text

    )

    print()