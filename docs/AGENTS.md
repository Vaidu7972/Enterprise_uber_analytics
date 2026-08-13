# UberOps AI Specialist Agents Guide

## 🤖 Agent Roles & Responsibilities

### 1. Supervisor Agent (`agentic_ai/agents/supervisor_agent.py`)
- Entry point for all incoming user questions.
- Invokes `classify_question` to determine intent, target entity, metric, and routing reason.
- Routes execution across General AI, Data Agent, Support Agent, ML Agent, or Multi-Agent graph.

### 2. Data Agent (`agentic_ai/agents/data_agent.py`)
- Queries PostgreSQL Gold Data Warehouse.
- Reads `information_schema.columns` to dynamically discover available tables and columns.
- Generates structured `SQLPlan` using Gemini.
- Enforces strict read-only SQL validation (blocks DDL/DML, restricts queries to `gold.*` schema).
- Includes automatic SQL error recovery loop (up to 2 retries).

### 3. Support Agent (`agentic_ai/agents/support_agent.py`)
- Answers policy, onboarding, accident SOP, and customer support queries using RAG.
- Performs Hybrid Retrieval across ChromaDB vector store.
- Returns grounded responses with exact source file and page attribution.

### 4. ML Agent (`agentic_ai/agents/ml_agent.py`)
- Invokes `predict_driver_risk` tool to retrieve real model prediction scores.
- Uses Gemini to synthesize clear business explanations without modifying probability scores.

### 5. Multi-Agent Orchestrator (`agentic_ai/graph/workflow.py`)
- LangGraph StateGraph coordinating multi-disciplinary investigations.
- Combines data evidence, ML predictions, and support policy guidelines.
- Computes deterministic business insights and formulates recommended operational actions.
