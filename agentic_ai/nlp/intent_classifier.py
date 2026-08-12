from google.genai import types

from agentic_ai.config.agent_config import GEMINI_MODEL

from agentic_ai.llm.gemini_client import client

from agentic_ai.nlp.intent_schema import QuestionIntent

from agentic_ai.prompts.intent_prompt import (
    INTENT_CLASSIFIER_PROMPT,
)


def classify_question(question: str) -> QuestionIntent:

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=question,
        config=types.GenerateContentConfig(
            system_instruction=INTENT_CLASSIFIER_PROMPT,
            response_mime_type="application/json",
            response_schema=QuestionIntent,
        ),
    )

    intent = QuestionIntent.model_validate_json(
        response.text
    )

    return intent