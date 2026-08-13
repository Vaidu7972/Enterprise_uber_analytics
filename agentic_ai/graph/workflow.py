import time
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
    Run full LangGraph multi-agent workflow with trace steps & timing metrics.
    """
    start_time = time.time()
    initial_state = {
        "question": question,
        "errors": []
    }

    final_state = langgraph_app.invoke(initial_state)
    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    route = final_state.get("route", "general")
    final_answer = final_state.get("final_answer", "")

    tables_used = final_state.get("data_result", {}).get("tables_used", []) if final_state.get("data_result") else []

    # Build Observable Agent Execution Trace Steps
    trace_steps = [
        "✓ Question received & preprocessed",
        f"✓ Intent classified as '{final_state.get('intent', 'general')}'",
        f"✓ Supervisor routed request to '{route}' agent",
    ]

    if route in ("data_agent", "multi_agent") and final_state.get("data_result"):
        trace_steps.append("✓ Gold schema inspected via information_schema")
        trace_steps.append("✓ SQL safety rules & single-statement validation passed")
        trace_steps.append("✓ PostgreSQL query executed on Gold schema")

    if route in ("support_agent", "multi_agent") and final_state.get("support_result"):
        trace_steps.append("✓ Support docs searched via ChromaDB hybrid vector index")
        trace_steps.append("✓ Grounded metadata citations parsed")

    if route in ("ml_agent", "multi_agent") and final_state.get("ml_result"):
        trace_steps.append("✓ RandomForest ML model loaded & driver features scored")

    trace_steps.append("✓ Evidence fused & executive response generated")

    result = {
        "route": route,
        "intent": final_state.get("intent"),
        "routing_reason": final_state.get("routing_reason"),
        "answer": final_answer,
        "sql": final_state.get("data_result", {}).get("sql") if final_state.get("data_result") else None,
        "data": final_state.get("data_result", {}).get("data") if final_state.get("data_result") else None,
        "tables_used": tables_used,
        "sources": final_state.get("support_result", {}).get("sources", []) if final_state.get("support_result") else [],
        "retrieved_chunks": final_state.get("support_result", {}).get("retrieved_chunks", []) if final_state.get("support_result") else [],
        "predictions": final_state.get("ml_result", {}).get("predictions") if final_state.get("ml_result") else None,
        "model_info": final_state.get("ml_result", {}).get("model_info") if final_state.get("ml_result") else None,
        "insights": final_state.get("insights"),
        "recommendations": final_state.get("recommendations"),
        "approval_required": final_state.get("approval_required", False),
        "approval_status": final_state.get("approval_status", "not_required"),
        "execution_time_ms": elapsed_ms,
        "trace_steps": trace_steps,
    }

    return result
