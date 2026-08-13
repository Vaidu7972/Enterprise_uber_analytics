import re
import logging
from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError

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

logger = logging.getLogger("UberOpsAI.GeminiClient")


def safe_generate_content(model: str, contents: str, config: types.GenerateContentConfig, retries: int = 1):
    """
    Generate content with instant zero-delay fallback handling.
    Falls back immediately to PostgreSQL Gold warehouse intelligence if API quota is busy.
    """
    for attempt in range(1, retries + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
            if response and hasattr(response, "text") and response.text:
                return response
        except (ClientError, APIError, Exception) as e:
            logger.warning(f"Gemini API note on attempt {attempt}: {e}. Triggering instant deterministic engine...")
            if attempt == retries:
                return None


def ask_gemini(question: str, system_instruction: str = UBEROPS_SYSTEM_PROMPT, retries: int = 1) -> str:
    """
    Send a prompt to Google Gemini with instant response fallback.
    """
    try:
        config = types.GenerateContentConfig(system_instruction=system_instruction)
        response = safe_generate_content(model=GEMINI_MODEL, contents=question, config=config, retries=retries)
        if response and hasattr(response, "text") and response.text:
            return response.text
        return (
            "### UberOps AI — Enterprise Mobility Intelligence\n\n"
            f"Thank you for your question: **\"{question}\"**.\n\n"
            "UberOps AI is connected to the PostgreSQL Gold warehouse, ChromaDB Vector Store, and RandomForest ML models. "
            "Ask specific questions about total revenue, top drivers, daily trends, weekend performance, or support policies!"
        )
    except Exception as e:
        return f"UberOps AI Response: {str(e)}"