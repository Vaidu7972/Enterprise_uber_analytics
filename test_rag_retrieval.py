from agentic_ai.rag.vector_store import (
    search_support_docs,
)


question = input(
    "Ask a support question: "
)


results = search_support_docs(
    question,
    top_k=3
)


print(
    "\n--- RETRIEVED CHUNKS ---"
)


for index, result in enumerate(
    results,
    start=1
):

    print(
        f"\nResult {index}"
    )

    print(
        "Source:",
        result["source"]
    )

    print(
        "Page:",
        result["page"]
    )

    print(
        "Distance:",
        result["distance"]
    )

    print(
        "\nText:"
    )

    print(
        result["text"]
    )