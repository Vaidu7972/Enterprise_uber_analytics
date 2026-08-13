from pathlib import Path

import chromadb

from agentic_ai.rag.embedding_service import (
    embed_texts,
    embed_query,
)


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
)


CHROMA_DIR = (
    BASE_DIR
    / "vector_store"
    / "chroma_db"
)


CHROMA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


chroma_client = (
    chromadb.PersistentClient(
        path=str(
            CHROMA_DIR
        )
    )
)


collection = (
    chroma_client
    .get_or_create_collection(
        name="uberops_support_docs",
        metadata={
            "description":
                "UberOps support and policy documents"
        }
    )
)


def index_chunks(
    chunks: list[dict]
):

    if not chunks:
        raise ValueError(
            "No chunks were provided."
        )

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = embed_texts(
        texts
    )

    ids = [
        chunk["id"]
        for chunk in chunks
    ]

    metadatas = []

    for chunk in chunks:

        metadatas.append(
            {
                "source":
                    chunk["source"],

                "page":
                    int(
                        chunk["page"]
                    ),

                "chunk_number":
                    int(
                        chunk[
                            "chunk_number"
                        ]
                    ),
            }
        )

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )


def search_support_docs(
    query: str,
    top_k: int = 4
) -> list[dict]:
    """
    Hybrid retrieval: Combines vector semantic search with keyword matching.
    """
    total_records = collection.count()

    if total_records == 0:
        raise RuntimeError(
            "Vector database is empty. Build the RAG index first."
        )

    # 1. Vector Semantic Search (retrieve candidates)
    candidate_k = min(top_k * 3, total_records)
    query_embedding = embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=candidate_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    # 2. Keyword Match Scoring
    keywords = [kw.lower() for kw in query.split() if len(kw) > 2]
    
    candidates = []
    max_dist = max(distances) if distances and max(distances) > 0 else 1.0

    for doc, meta, dist in zip(documents, metadatas, distances):
        # Semantic score (0 to 1, higher is better)
        semantic_score = 1.0 - (dist / (max_dist + 1e-5))

        # Keyword match score
        doc_lower = doc.lower()
        keyword_hits = sum(1 for kw in keywords if kw in doc_lower)
        keyword_score = keyword_hits / (len(keywords) + 1e-5) if keywords else 0.0

        # Combined Hybrid Score
        hybrid_score = (0.7 * semantic_score) + (0.3 * keyword_score)

        candidates.append({
            "text": doc,
            "source": meta["source"],
            "page": meta["page"],
            "chunk_number": meta["chunk_number"],
            "distance": float(dist),
            "semantic_score": float(semantic_score),
            "keyword_score": float(keyword_score),
            "hybrid_score": float(hybrid_score),
        })

    # Sort candidates by hybrid score descending
    candidates.sort(key=lambda x: x["hybrid_score"], reverse=True)
    return candidates[:top_k]