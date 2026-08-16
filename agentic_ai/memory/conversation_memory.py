import re
from typing import Dict, Any, Optional

_SESSION_MEMORY: Dict[str, Dict[str, Any]] = {}

def get_session_memory(session_id: str = "default_session") -> Dict[str, Any]:
    """Retrieve session-level memory state."""
    if session_id not in _SESSION_MEMORY:
        _SESSION_MEMORY[session_id] = {
            "last_driver_id": None,
            "last_customer_id": None,
            "last_city": None,
            "last_metric": None,
            "conversation_history": []
        }
    return _SESSION_MEMORY[session_id]

def update_session_memory(
    session_id: str = "default_session",
    driver_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    city: Optional[str] = None,
    metric: Optional[str] = None,
    user_query: Optional[str] = None,
    ai_response: Optional[str] = None
):
    """Update session memory with entity context and dialogue turns."""
    mem = get_session_memory(session_id)
    if driver_id:
        mem["last_driver_id"] = driver_id.upper()
    if customer_id:
        mem["last_customer_id"] = customer_id.upper()
    if city:
        mem["last_city"] = city.title()
    if metric:
        mem["last_metric"] = metric

    if user_query or ai_response:
        mem["conversation_history"].append({
            "user": user_query,
            "ai": ai_response
        })
        # Prune conversation history to recent 10 turns
        if len(mem["conversation_history"]) > 10:
            mem["conversation_history"] = mem["conversation_history"][-10:]

def resolve_entity_in_question(question: str, session_id: str = "default_session") -> str:
    """
    Pronominal entity resolution: Replace pronouns ('he', 'his', 'that driver')
    with the last referenced driver_id or customer_id in session memory.
    """
    mem = get_session_memory(session_id)
    last_d = mem.get("last_driver_id")
    
    # Check explicit driver mention first
    words = question.replace("?", "").replace(",", "").split()
    for w in words:
        if w.upper().startswith("D") and len(w) >= 3 and w[1:].isdigit():
            update_session_memory(session_id=session_id, driver_id=w.upper())
            return question

    if not last_d:
        return question

    # Replace pronouns with explicit driver ID
    resolved_q = question
    pronoun_patterns = [
        (r'\b(he|him|his|that driver|the driver)\b', last_d)
    ]
    for pattern, replacement in pronoun_patterns:
        resolved_q = re.sub(pattern, f"driver {replacement}", resolved_q, flags=re.IGNORECASE)

    return resolved_q
