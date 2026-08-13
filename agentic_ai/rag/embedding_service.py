from google.genai import types

from agentic_ai.config.agent_config import (
    GEMINI_EMBEDDING_MODEL,
)

from agentic_ai.llm.gemini_client import (
    client,
)


EMBEDDING_DIMENSION = 768


def embed_texts(
    texts: list[str]
) -> list[list[float]]:

    if not texts:
        return []

    response = client.models.embed_content(
        model=GEMINI_EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(
            output_dimensionality=
                EMBEDDING_DIMENSION
        ),
    )

    embeddings = []

    for embedding in response.embeddings:

        embeddings.append(
            list(
                embedding.values
            )
        )

    return embeddings


def embed_query(
    query: str
) -> list[float]:

    embeddings = embed_texts(
        [query]
    )

    return embeddings[0]