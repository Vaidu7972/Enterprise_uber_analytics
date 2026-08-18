from google.genai import types
from agentic_ai.config.agent_config import GEMINI_MODEL
from agentic_ai.llm.gemini_client import safe_generate_content
from agentic_ai.nlp.intent_schema import QuestionIntent                   
from agentic_ai.prompts.intent_prompt import INTENT_CLASSIFIER_PROMPT     #instrruction

#rule based  classification  multi > ML > support >data > general 

def classify_question(question: str) -> QuestionIntent:
    """
    Classify natural language questions into agent routes instantly using deterministic rules,
    with Gemini LLM API fallback for complex open-ended queries.
    """
    q_lower = question.lower()

    # Instant Zero-Delay Keyword Classification (0.1ms)
    if ("why" in q_lower or "investigate" in q_lower) and ("driver" in q_lower or "underperform" in q_lower):
        return QuestionIntent(
            route="multi_agent",
            intent="multi_agent_query",
            routing_reason="Multi-agent investigation for driver performance cause, prediction, and recommendation.",
        )
    elif any(kw in q_lower for kw in ["predict", "prediction", "underperform", "underperformance", "risk", "likely to", "ml", "model"]):
        return QuestionIntent(
            route="ml_agent",
            intent="ml_query",
            routing_reason="ML driver underperformance risk assessment.",
        )
    elif any(kw in q_lower for kw in ["policy", "onboard", "onboarding", "accident", "sop", "cancel", "cancellation", "faq", "document", "documents", "requirement", "requirements", "support", "rules"]):
        return QuestionIntent(
            route="support_agent",
            intent="support_query",
            routing_reason="Support knowledge base policy retrieval.",
        )
    elif any(kw in q_lower for kw in ["revenue", "trip", "trips", "total", "fare", "count", "gold", "customer", "customers", "driver", "drivers", "top", "rank", "kpi", "weekday", "weekend", "average", "avg", "mart", "warehouse", "fact", "city", "rating", "ratings"]):
        return QuestionIntent(
            route="data_agent",
            intent="data_query",
            routing_reason="PostgreSQL Gold warehouse analytics query.",
        )

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
    except Exception:
        pass

    return QuestionIntent(
        route="general",
        intent="general_query",
        routing_reason="General AI response route.",
    )