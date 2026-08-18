import json
from google.genai import types     #configure gemini 
from agentic_ai.config.agent_config import GEMINI_MODEL    # no need to mention model gemini again and again
from agentic_ai.llm.gemini_client import safe_generate_content    #gemini wrapper (abstraction)
from agentic_ai.tools.ml_tool import predict_driver_risk

ML_AGENT_PROMPT = """
You are the ML Intelligence Agent for UberOps AI.
Your responsibility is to explain predictive Machine Learning results to business managers and operational leads.

CRITICAL RULES:
1. You MUST NOT invent, guess, or modify ML probability scores or metrics.
2. Rely strictly on the model prediction dictionary provided in the context.
3. Clearly state the driver's risk level (High, Medium, Low), key contributing features, and operational recommendations.
4. Keep the explanation professional, quantitative, clear, and actionable.
"""


def answer_ml_question(question: str, driver_id: str = None) -> dict:
    """
    ML Agent workflow:
    1. Extract potential driver_id from question if provided.
    2. Call predict_driver_risk ML tool.
    3. Synthesize business explanation via Gemini.
    """
    if not driver_id:
        words = question.replace("?", "").replace(",", "").split()
        for w in words:    #check every word
            if w.upper().startswith("D") and len(w) >= 3 and w[1:].isdigit():    #3condition for driver id
                driver_id = w.upper()
                break

    ml_result = predict_driver_risk(driver_id=driver_id)     

    prompt = f"""
USER QUESTION:
{question}

ML PREDICTION RESULT:
{json.dumps(ml_result, indent=2, default=str)}    # ml tool returns a Python dictionary

Provide a concise, professional business breakdown explaining the ML risk predictions, the driver rating/trip factors driving the score, and key operational takeaways.
"""
#calling Gemini
    response = safe_generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=ML_AGENT_PROMPT
        ),
    )

    if response and hasattr(response, "text") and response.text:
        answer_text = response.text
    else:
        if ml_result.get("found") and ml_result.get("mode") != "batch":
            answer_text = f"### 🤖 ML Risk Prediction Analysis\n\n- **Driver ID:** `{ml_result.get('driver_id')}` ({ml_result.get('driver_name')})\n- **Risk Level:** **{ml_result.get('risk_level')}**\n- **Underperformance Probability:** **{round(ml_result.get('risk_probability', 0)*100, 2)}%**\n- **Driver Rating:** `{ml_result.get('rating')}` | **Total Trips:** `{ml_result.get('total_trips')}` | **Average Fare:** `${ml_result.get('average_fare')}`\n\n*Actionable Takeaway:* Driver is evaluated based on trained RandomForest model features."
        else:
            answer_text = f"### 🤖 ML Risk Batch Scoring\n\n- **Scored Drivers:** `{ml_result.get('total_drivers_scored')}`\n- **High Risk Count:** `{ml_result.get('high_risk_count')}`\n- **Medium Risk Count:** `{ml_result.get('medium_risk_count')}`\n- **Low Risk Count:** `{ml_result.get('low_risk_count')}`"

    return {
        "answer": answer_text,
        "predictions": ml_result,
        "model_info": ml_result.get("model_info", {}),
        "features_used": ml_result.get("features_used", {})
    }

# ml_agent.py --> Ml tool -->random Forest Prediction (risk probablity + feature)