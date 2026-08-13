from agentic_ai.agents.support_agent import (
    answer_support_question,
)


question = input(
    "Ask UberOps Support: "
)


try:

    result = answer_support_question(
        question
    )

    print(
        "\n--- SUPPORT ANSWER ---"
    )

    print(
        result["answer"]
    )

    print(
        "\n--- SOURCES ---"
    )

    for source in result["sources"]:

        print(
            f'- {source["source"]} '
            f'(Page {source["page"]})'
        )

    print(
        "\n--- RETRIEVED CHUNKS ---"
    )

    for chunk in result[
        "retrieved_chunks"
    ]:

        print(
            "\n-----------------------"
        )

        print(
            "Source:",
            chunk["source"]
        )

        print(
            "Page:",
            chunk["page"]
        )

        print(
            "Distance:",
            chunk["distance"]
        )

        print(
            chunk["text"]
        )

except Exception as error:

    print(
        "\nSupport Agent Error:"
    )

    print(
        error
    )