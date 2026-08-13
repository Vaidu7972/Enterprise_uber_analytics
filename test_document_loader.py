from pathlib import Path

from agentic_ai.rag.document_loader import (
    load_support_documents,
)


BASE_DIR = Path(__file__).resolve().parent

DOCS_DIR = (
    BASE_DIR
    / "data"
    / "support_docs"
)


documents = load_support_documents(
    DOCS_DIR
)


print(
    "Documents/pages loaded:",
    len(documents)
)


for document in documents:

    print("\n--------------------")

    print(
        "Source:",
        document["source"]
    )

    print(
        "Page:",
        document["page"]
    )

    print(
        document["text"][:300]
    )