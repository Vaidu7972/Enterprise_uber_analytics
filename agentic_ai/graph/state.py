from typing import TypedDict, Optional, List, Dict, Any

class AgentState(TypedDict, total=False):
    question: str
    route: str
    intent: str
    routing_reason: str
    
    data_result: Optional[Dict[str, Any]]
    support_result: Optional[Dict[str, Any]]
    ml_result: Optional[Dict[str, Any]]
    
    insights: Optional[Dict[str, Any]]
    recommendations: Optional[Dict[str, Any]]
    
    approval_required: bool
    approval_status: str  # "pending", "approved", "rejected"
    
    final_answer: str
    errors: List[str]
