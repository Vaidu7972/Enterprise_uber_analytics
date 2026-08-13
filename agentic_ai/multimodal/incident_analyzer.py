from google.genai import types
from agentic_ai.config.agent_config import GEMINI_MODEL
from agentic_ai.llm.gemini_client import client, safe_generate_content

INCIDENT_ANALYSIS_PROMPT = """
You are the Multimodal Incident & Damage Analyzer for UberOps AI.
Your job is to analyze uploaded vehicle images, incident documentation, or audio descriptions.

CRITICAL ADVISORY DISCLAIMER:
You MUST include this disclaimer at the top of your assessment:
'⚠️ ADVISORY DISCLAIMER: AI image and incident analysis is provided for preliminary guidance only and does NOT constitute an official insurance appraisal or physical vehicle damage assessment.'

Analyze the provided inputs objectively and provide:
1. Preliminary Damage Assessment
2. Estimated Severity Level (Low, Medium, High, Severe)
3. SOP Compliance & Incident Reporting Steps
"""

def analyze_incident_multimodal(description: str = "", image_bytes: bytes = None, image_mime: str = "image/jpeg") -> dict:
    """
    Multimodal analysis module using Gemini Vision API.
    """
    contents = []
    
    if image_bytes:
        contents.append(
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=image_mime,
            )
        )

    text_prompt = f"INCIDENT DESCRIPTION: {description if description else 'Please analyze the attached vehicle incident image.'}"
    contents.append(text_prompt)

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=INCIDENT_ANALYSIS_PROMPT
            ),
        )
        answer = response.text
    except Exception as e:
        answer = f"⚠️ ADVISORY DISCLAIMER: AI image and incident analysis is provided for preliminary guidance only.\n\nMultimodal Analysis Note: {str(e)}"

    return {
        "assessment": answer,
        "disclaimer": "AI image and incident analysis is advisory and not an authoritative insurance appraisal."
    }
