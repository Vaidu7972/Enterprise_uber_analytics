from agentic_ai.nlp.intent_classifier import classify_question
from agentic_ai.llm.gemini_client import ask_gemini
from agentic_ai.agents.data_agent import answer_data_question
from agentic_ai.agents.support_agent import answer_support_question
from agentic_ai.agents.ml_agent import answer_ml_question
from agentic_ai.engine.insight_engine import generate_business_insights
from agentic_ai.engine.action_engine import formulate_recommendations
from agentic_ai.memory.persistent_memory import log_agent_activity
from agentic_ai.graph.state import AgentState


def supervisor_node(state: AgentState) -> AgentState:
    question = state["question"]
    intent = classify_question(question)
    
    return {
        **state,
        "route": intent.route,
        "intent": intent.intent,
        "routing_reason": intent.routing_reason,
    }


def general_agent_node(state: AgentState) -> AgentState:
    answer = ask_gemini(state["question"])
    log_agent_activity(state["question"], "general", "General AI")
    return {
        **state,
        "final_answer": answer
    }


def data_agent_node(state: AgentState) -> AgentState:
    res = answer_data_question(state["question"])
    log_agent_activity(state["question"], "data_agent", "Data Agent", tool_used="PostgreSQL Gold")
    return {
        **state,
        "data_result": res,
        "final_answer": res["answer"]
    }


def support_agent_node(state: AgentState) -> AgentState:
    res = answer_support_question(state["question"])
    log_agent_activity(state["question"], "support_agent", "Support Agent", tool_used="ChromaDB RAG")
    return {
        **state,
        "support_result": res,
        "final_answer": res["answer"]
    }


def ml_agent_node(state: AgentState) -> AgentState:
    res = answer_ml_question(state["question"])
    log_agent_activity(state["question"], "ml_agent", "ML Agent", tool_used="RandomForest ML Model")
    return {
        **state,
        "ml_result": res,
        "final_answer": res["answer"]
    }


def multi_agent_node(state: AgentState) -> AgentState:
    question = state["question"]

    # 1. Execute Data Agent
    data_res = answer_data_question(question)

    # 2. Execute ML Agent
    ml_res = answer_ml_question(question)

    # 3. Execute Support Agent
    support_res = answer_support_question(question)

    # 4. Generate Combined Insights & Action Recommendations
    insights = generate_business_insights(data_result=data_res, ml_result=ml_res, support_result=support_res)
    recs = formulate_recommendations(question, data_result=data_res, ml_result=ml_res, support_result=support_res)

    # Synthesis report
    final_report = f"""### 🚕 UberOps AI Multi-Agent Investigation Report

#### 📊 Warehouse Data Evidence
{data_res.get('answer', 'No warehouse data available.')}

#### 🤖 Predictive ML Findings
{ml_res.get('answer', 'No ML prediction available.')}

#### 📚 Support Policy Evidence
{support_res.get('answer', 'No support policy available.')}

#### 💡 Combined Business Insights
{insights['insight_summary']}

#### 🎯 Recommended Action
{recs['primary_recommendation']}
"""

    log_agent_activity(
        question=question,
        route="multi_agent",
        agent="LangGraph Supervisor",
        tool_used="Multi-Agent Orchestration",
        action_recommended=recs["primary_recommendation"],
        approval_status="PENDING" if recs["approval_required"] else "NOT_REQUIRED"
    )

    return {
        **state,
        "data_result": data_res,
        "ml_result": ml_res,
        "support_result": support_res,
        "insights": insights,
        "recommendations": recs,
        "approval_required": recs["approval_required"],
        "approval_status": "pending" if recs["approval_required"] else "not_required",
        "final_answer": final_report
    }
