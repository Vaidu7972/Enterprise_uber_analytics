from google import genai
from google.genai import types

from agentic_ai.config.agent_config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
)

from agentic_ai.prompts.system_prompt import (
    UBEROPS_SYSTEM_PROMPT,
)


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def ask_gemini(question: str) -> str:

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=question,
        config=types.GenerateContentConfig(
            system_instruction=UBEROPS_SYSTEM_PROMPT
        )
    )

    return response.text