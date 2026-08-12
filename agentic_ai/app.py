from agentic_ai.llm.gemini_client import ask_gemini


def main():

    print("=" * 60)
    print("UBEROPS AI")
    print("Agentic Data Intelligence & Support Platform")
    print("=" * 60)

    while True:

        question = input(
            "\nAsk UberOps AI a question "
            "(type 'exit' to stop): "
        )

        if question.lower() == "exit":
            print("\nUberOps AI stopped.")
            break

        if not question.strip():
            print("Please enter a question.")
            continue

        try:

            print("\nThinking...\n")

            answer = ask_gemini(question)

            print("UberOps AI:")
            print(answer)

        except Exception as e:

            print("\nSomething went wrong:")
            print(e)


if __name__ == "__main__":
    main()