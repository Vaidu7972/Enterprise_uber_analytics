import re
import logging
import time
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


def parse_retry_delay(error_str: str) -> int:
    """Extract retry delay seconds from Gemini 429 error message."""
    try:
        matches = re.findall(r"(\d+\.?\d*)\s*s\b", error_str, re.IGNORECASE) or \
                  re.findall(r"retry(?:Delay|In)?:?\s*['\"]?(\d+\.?\d*)", error_str, re.IGNORECASE)
        if matches:
            val = float(matches[0])
            return max(5, int(val) + 3)
    except Exception:
        pass
    return 15


def safe_generate_content(model: str, contents: str, config: types.GenerateContentConfig, retries: int = 6):
    """
    Generate content with robust rate limit backoff handling (429 Resource Exhausted).
    Returns response object or None if retries exhausted.
    """
    for attempt in range(1, retries + 1):
        try:
            time.sleep(1.2)
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
            return response
        except (ClientError, APIError, Exception) as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "Quota exceeded" in err_str:
                delay = parse_retry_delay(err_str)
                logger.warning(f"Gemini Rate Limit (429). Waiting {delay}s before retry {attempt}/{retries}...")
                time.sleep(delay)
            else:
                logger.warning(f"Gemini API call error on attempt {attempt}: {e}")
                time.sleep(2)
            if attempt == retries:
                logger.error(f"Exhausted {retries} retries on Gemini API call: {e}")
                return None


def ask_gemini(question: str, system_instruction: str = UBEROPS_SYSTEM_PROMPT, retries: int = 4) -> str:
    """
    Send a prompt to Google Gemini with automatic retry and rate limit backoff.
    """
    try:
        config = types.GenerateContentConfig(system_instruction=system_instruction)
        response = safe_generate_content(model=GEMINI_MODEL, contents=question, config=config, retries=retries)
        if response and hasattr(response, "text") and response.text:
            return response.text
        return "The Gemini LLM service is temporarily busy due to free-tier API rate limits. Please try again in a few moments."
    except Exception as e:
        return f"*(Gemini API Note: Service busy. {str(e)})*"