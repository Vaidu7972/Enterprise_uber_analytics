from agentic_ai.agents.data_agent import (
    answer_data_question,
)


question = input(
    "Ask a data question: "
)


try:

    result = answer_data_question(
        question
    )

    print("\n--- GENERATED SQL ---")

    print(
        result["sql"]
        if result["sql"]
        else "No SQL generated"
    )

    print("\n--- DATA ---")

    if result["data"] is not None:

        print(
            result["data"].to_string(
                index=False
            )
        )

    else:

        print("No database result")

    print("\n--- UBEROPS ANSWER ---")

    print(
        result["answer"]
    )

except Exception as e:

    print("\nData Agent Error:")
    print(e)