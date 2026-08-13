from langgraph.graph import StateGraph, END
from agentic_ai.graph.state import AgentState
from agentic_ai.graph.nodes import (
    supervisor_node,
    general_agent_node,
    data_agent_node,
    support_agent_node,
    ml_agent_node,
    multi_agent_node
)


def route_decision(state: AgentState) -> str:
    return state.get("route", "general")


# Build LangGraph StateGraph
builder = StateGraph(AgentState)

builder.add_node("supervisor", supervisor_node)
builder.add_node("general", general_agent_node)
builder.add_node("data_agent", data_agent_node)
builder.add_node("support_agent", support_agent_node)
builder.add_node("ml_agent", ml_agent_node)
builder.add_node("multi_agent", multi_agent_node)

builder.set_entry_point("supervisor")

builder.add_conditional_edges(
    "supervisor",
    route_decision,
    {
        "general": "general",
        "data_agent": "data_agent",
        "support_agent": "support_agent",
        "ml_agent": "ml_agent",
        "multi_agent": "multi_agent",
    }
)

builder.add_edge("general", END)
builder.add_edge("data_agent", END)
builder.add_edge("support_agent", END)
builder.add_edge("ml_agent", END)
builder.add_edge("multi_agent", END)

# Compile graph
langgraph_app = builder.compile()


def run_orchestration(question: str) -> dict:
    """
    Run full LangGraph multi-agent workflow.
    """
    initial_state = {
        "question": question,
        "errors": []
    }

    final_state = langgraph_app.invoke(initial_state)

    route = final_state.get("route", "general")
    final_answer = final_state.get("final_answer", "")

    # Format into standard response schema
    result = {
        "route": route,
        "intent": final_state.get("intent"),
        "routing_reason": final_state.get("routing_reason"),
        "answer": final_answer,
        "sql": final_state.get("data_result", {}).get("sql") if final_state.get("data_result") else None,
        "data": final_state.get("data_result", {}).get("data") if final_state.get("data_result") else None,
        "tables_used": final_state.get("data_result", {}).get("tables_used", []) if final_state.get("data_result") else [],
        "sources": final_state.get("support_result", {}).get("sources", []) if final_state.get("support_result") else [],
        "retrieved_chunks": final_state.get("support_result", {}).get("retrieved_chunks", []) if final_state.get("support_result") else [],
        "predictions": final_state.get("ml_result", {}).get("predictions") if final_state.get("ml_result") else None,
        "model_info": final_state.get("ml_result", {}).get("model_info") if final_state.get("ml_result") else None,
        "insights": final_state.get("insights"),
        "recommendations": final_state.get("recommendations"),
        "approval_required": final_state.get("approval_required", False),
        "approval_status": final_state.get("approval_status", "not_required")
    }

    return result
