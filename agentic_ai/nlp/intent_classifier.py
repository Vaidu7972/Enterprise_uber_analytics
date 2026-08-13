from google.genai import types

from agentic_ai.config.agent_config import GEMINI_MODEL

from agentic_ai.llm.gemini_client import client

from agentic_ai.nlp.intent_schema import QuestionIntent

from agentic_ai.prompts.intent_prompt import (
    INTENT_CLASSIFIER_PROMPT,
)


from agentic_ai.llm.gemini_client import safe_generate_content

def classify_question(question: str) -> QuestionIntent:
    try:
        response = safe_generate_content(
            model=GEMINI_MODEL,
            contents=question,
            config=types.GenerateContentConfig(
                system_instruction=INTENT_CLASSIFIER_PROMPT,
                response_mime_type="application/json",
                response_schema=QuestionIntent,
            ),
        )
        if response and hasattr(response, "text") and response.text:
            return QuestionIntent.model_validate_json(response.text)
    except Exception as e:
        pass

    # Deterministic Keyword Fallback Classifier
    q_lower = question.lower()
    if any(kw in q_lower for kw in ["revenue", "trip", "total", "fare", "count", "gold", "customer"]):
        return QuestionIntent(
            route="data_agent",
            intent="data_query",
            routing_reason="Keyword-based classification fallback for data warehouse analytics."
        )
    elif any(kw in q_lower for kw in ["policy", "onboard", "accident", "sop", "cancel", "faq", "document", "paper"]):
        return QuestionIntent(
            route="support_agent",
            intent="support_query",
            routing_reason="Keyword-based classification fallback for support policy search."
        )
    elif any(kw in q_lower for kw in ["underperform", "risk", "predict", "ml", "rating"]):
        return QuestionIntent(
            route="ml_agent",
            intent="ml_query",
            routing_reason="Keyword-based classification fallback for ML driver risk assessment."
        )
    elif "why" in q_lower and "driver" in q_lower:
        return QuestionIntent(
            route="multi_agent",
            intent="multi_agent_query",
            routing_reason="Keyword-based classification fallback for multi-agent driver investigation."
        )

    return QuestionIntent(
        route="general",
        intent="general_query",
        routing_reason="General AI response route."
    )
