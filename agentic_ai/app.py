from agentic_ai.agents.supervisor_agent import (
    handle_question,
)


def main():

    print("=" * 60)
    print("UBEROPS AI")
    print(
        "Agentic Data Intelligence "
        "& Support Platform"
    )
    print("=" * 60)

    while True:

        question = input(
            "\nAsk UberOps AI "
            "(type 'exit' to stop): "
        )

        if question.lower() == "exit":

            print(
                "\nUberOps AI stopped."
            )

            break

        if not question.strip():

            print(
                "Please enter a question."
            )

            continue

        try:

            print(
                "\nAnalyzing question...\n"
            )

            result = handle_question(
                question
            )

            print(
                "Route:",
                result["route"]
            )

            print(
                "Intent:",
                result["intent"]
            )

            print(
                "Reason:",
                result["routing_reason"]
            )

            # Show SQL if Data Agent was used
            if result["sql"]:

                print(
                    "\n--- GENERATED SQL ---"
                )

                print(
                    result["sql"]
                )

            # Show database data if available
            if result["data"] is not None:

                print(
                    "\n--- DATABASE RESULT ---"
                )

                print(
                    result["data"]
                    .head(20)
                    .to_string(index=False)
                )

            print(
                "\n--- UBEROPS ANSWER ---"
            )

            print(
                result["answer"]
            )

        except Exception as e:

            print(
                "\nSomething went wrong:"
            )

            print(e)


if __name__ == "__main__":
    main()