from dotenv import load_dotenv

from openai import OpenAI

from app.services.embedding_service import EmbeddingService

import math

load_dotenv()

client = OpenAI()

embedding_service = EmbeddingService(

    client=client

)

texts = [

    "Machine learning can detect temperature anomalies.",

    "AI models can identify abnormal temperature changes.",

    "Cristiano Ronaldo is a football player."

]

vectors = embedding_service.embed(texts)

print("Number of texts:", len(texts))

print("Number of vectors:", len(vectors))

print()

for i, vector in enumerate(vectors):

    print(

        f"Text {i + 1}:",

        texts[i]

    )

    print(

        "Vector dimension:",

        len(vector)

    )

    print(

        "First 5 values:",

        vector[:5]

    )

    print()

def cosine_similarity(

    vector_a: list[float],

    vector_b: list[float]

) -> float:

    dot_product = sum(

        a * b

        for a, b in zip(vector_a, vector_b)

    )

    magnitude_a = math.sqrt(

        sum(a * a for a in vector_a)

    )

    magnitude_b = math.sqrt(

        sum(b * b for b in vector_b)

    )

    return dot_product / (

        magnitude_a * magnitude_b

    )

print(

    "Text 1 <-> Text 2:",

    cosine_similarity(

        vectors[0],

        vectors[1]

    )

)

print(

    "Text 1 <-> Text 3:",

    cosine_similarity(

        vectors[0],

        vectors[2]

    )

)

print(

    "Text 2 <-> Text 3:",

    cosine_similarity(

        vectors[1],

        vectors[2]

    )

)