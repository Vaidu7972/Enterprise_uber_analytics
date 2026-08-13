from agentic_ai.rag.embedding_service import (
    embed_query,
)


text = (
    "Driver must report an accident."
)


embedding = embed_query(
    text
)


print(
    "Embedding dimensions:",
    len(embedding)
)


print(
    "First 10 values:"
)

print(
    embedding[:10]
)