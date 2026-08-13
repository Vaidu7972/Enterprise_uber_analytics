from pathlib import Path

from agentic_ai.rag.document_loader import (
    load_support_documents,
)

from agentic_ai.rag.chunker import (
    chunk_documents,
)

from agentic_ai.rag.vector_store import (
    index_chunks,
    collection,
)


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
)


DOCS_DIR = (
    BASE_DIR
    / "data"
    / "support_docs"
)


def build_rag_index():

    print(
        "Loading support documents..."
    )

    documents = (
        load_support_documents(
            DOCS_DIR
        )
    )

    print(
        "Pages/documents loaded:",
        len(documents)
    )


    print(
        "Creating chunks..."
    )

    chunks = chunk_documents(
        documents,
        chunk_size=220,
        overlap=40
    )

    print(
        "Chunks created:",
        len(chunks)
    )


    print(
        "Creating embeddings "
        "and indexing in ChromaDB..."
    )

    index_chunks(
        chunks
    )


    print(
        "RAG index built successfully!"
    )

    print(
        "Total vector records:",
        collection.count()
    )


if __name__ == "__main__":

    build_rag_index()