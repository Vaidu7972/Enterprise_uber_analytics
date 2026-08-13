# UberOps AI Architecture Guide

## 🏗️ System Components

1. **Bronze -> Silver -> Gold Warehouse**:
   - Ingests Parquet trip data, JSON drivers, XML customers, and CSV weather data into PostgreSQL.
   - Cleans and transforms records into dimensional models (`gold.dim_driver`, `gold.dim_customer`, `gold.dim_weather`, `gold.dim_date`) and fact table (`gold.fact_trip`).
   - Aggregates performance into analytics marts (`gold.driver_performance_mart`, `gold.revenue_mart`, `gold.kpi_summary`).

2. **Gemini LLM Integration**:
   - `google-genai` SDK with `gemini-3.6-flash`.
   - Automatic rate limit backoff (429 handling).
   - Structured JSON schema validation via Pydantic (`SQLPlan`, `QuestionIntent`).

3. **LangGraph Multi-Agent Orchestration**:
   - StateGraph coordinating `supervisor_node`, `general_agent_node`, `data_agent_node`, `support_agent_node`, `ml_agent_node`, and `multi_agent_node`.
   - Conditional routing and error recovery.

4. **Predictive ML Engine**:
   - Scikit-learn RandomForest model for driver underperformance risk.
   - Feature engineering script aggregating rating, trip volume, revenue, fare, distance, and duration.

5. **Grounded Hybrid RAG Support Engine**:
   - ChromaDB vector database storing document chunks embedded with `gemini-embedding-001`.
   - Hybrid retrieval combining vector distance scoring and keyword match scoring.

6. **Audit & Reporting Engine**:
   - Persistent logging to `gold.agent_audit_logs`, `gold.action_logs`, `gold.investigation_logs`.
   - PDF report compilation via ReportLab.
