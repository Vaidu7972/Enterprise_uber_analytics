from agentic_ai.graph.workflow import run_orchestration


def handle_question(question: str) -> dict:
    """
    Supervisor Agent entry point. Routes questions dynamically
    using LangGraph multi-agent state graph orchestration.
    """
    return run_orchestration(question)     #send question to main langraph workflow
#then allocate agent 
