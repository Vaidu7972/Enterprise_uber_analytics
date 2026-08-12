from agentic_ai.nlp.intent_classifier import (
    classify_question,
)

from agentic_ai.llm.gemini_client import (
    ask_gemini,
)

from agentic_ai.agents.data_agent import (
    answer_data_question,
)


def handle_question(question: str) -> dict:

    # Step 1: Understand the user question
    intent = classify_question(question)

    # Common response structure
    result = {
        "route": intent.route,
        "intent": intent.intent,
        "routing_reason": intent.routing_reason,
        "answer": None,
        "sql": None,
        "data": None,
        "tables_used": [],
    }

    # ------------------------------------
    # GENERAL QUESTIONS
    # ------------------------------------

    if intent.route == "general":

        answer = ask_gemini(question)

        result["answer"] = answer

        return result

    # ------------------------------------
    # DATA QUESTIONS
    # ------------------------------------

    if intent.route == "data_agent":

        data_result = answer_data_question(
            question
        )

        result["answer"] = data_result[
            "answer"
        ]

        result["sql"] = data_result[
            "sql"
        ]

        result["data"] = data_result[
            "data"
        ]

        result["tables_used"] = data_result[
            "tables_used"
        ]

        return result

    # ------------------------------------
    # SUPPORT QUESTIONS
    # ------------------------------------

    if intent.route == "support_agent":

        result["answer"] = (
            "This question requires the "
            "Support Agent and RAG system. "
            "We will build that module next."
        )

        return result

    # ------------------------------------
    # ML QUESTIONS
    # ------------------------------------

    if intent.route == "ml_agent":

        result["answer"] = (
            "This question requires the "
            "ML Agent. The predictive ML "
            "module has not been built yet."
        )

        return result

    # ------------------------------------
    # MULTI-AGENT QUESTIONS
    # ------------------------------------

    if intent.route == "multi_agent":

        result["answer"] = (
            "This question requires multiple "
            "agents. Multi-agent orchestration "
            "will be implemented using "
            "LangGraph later."
        )

        return result

    # ------------------------------------
    # FALLBACK
    # ------------------------------------

    result["answer"] = (
        "UberOps AI could not determine "
        "the correct route for this question."
    )

    return result