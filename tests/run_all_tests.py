import sys
import time
import unittest
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from utils.db_connection import get_engine
from agentic_ai.tools.sql_tool import get_gold_schema, validate_read_only_sql, execute_read_only_query
from agentic_ai.nlp.intent_classifier import classify_question
from agentic_ai.agents.data_agent import answer_data_question
from agentic_ai.agents.support_agent import answer_support_question
from agentic_ai.rag.vector_store import search_support_docs, collection
from agentic_ai.tools.ml_tool import predict_driver_risk
from agentic_ai.graph.workflow import run_orchestration
from agentic_ai.reports.report_generator import generate_pdf_report


class TestUberOpsPlatform(unittest.TestCase):

    def test_01_database_connection(self):
        print("\n[TEST 1] Testing PostgreSQL Gold Warehouse Connection...")
        engine = get_engine()
        with engine.connect() as conn:
            self.assertTrue(conn is not None)
        print("  [OK] Database Connected Successfully")

    def test_02_gold_schema_discovery(self):
        print("\n[TEST 2] Testing Gold Schema Dynamic Discovery...")
        schema = get_gold_schema()
        self.assertIn("gold.dim_driver", schema)
        self.assertIn("gold.fact_trip", schema)
        print("  [OK] Gold Schema Discovered Successfully")

    def test_03_sql_safety_validator(self):
        print("\n[TEST 3] Testing SQL Safety Rules...")
        valid_sql = "SELECT * FROM gold.dim_driver LIMIT 5;"
        self.assertEqual(validate_read_only_sql(valid_sql), "SELECT * FROM gold.dim_driver LIMIT 5")

        with self.assertRaises(ValueError):
            validate_read_only_sql("DROP TABLE gold.fact_trip;")

        with self.assertRaises(ValueError):
            validate_read_only_sql("DELETE FROM gold.dim_driver;")

        with self.assertRaises(ValueError):
            validate_read_only_sql("UPDATE gold.dim_driver SET rating = 5;")

        print("  [OK] Read-Only SQL Safety Enforced Successfully")

    def test_04_intent_classifier(self):
        print("\n[TEST 4] Testing Gemini Intent Classifier...")
        time.sleep(3)
        res_data = classify_question("What is total revenue in the warehouse?")
        self.assertEqual(res_data.route, "data_agent")
        time.sleep(3)
        res_supp = classify_question("What documents are required for driver onboarding?")
        self.assertEqual(res_supp.route, "support_agent")
        print("  [OK] Intent Classifier Routing Verified")

    def test_05_data_agent(self):
        print("\n[TEST 5] Testing Data Agent PostgreSQL Query...")
        time.sleep(3)
        res = answer_data_question("What is total revenue?")
        self.assertIsNotNone(res.get("answer"))
        self.assertIsNotNone(res.get("sql"))
        print("  [OK] Data Agent Executed Real Query Successfully")

    def test_06_rag_hybrid_retrieval(self):
        print("\n[TEST 6] Testing Support Agent RAG Retrieval...")
        self.assertGreater(collection.count(), 0)
        chunks = search_support_docs("accident policy SOP", top_k=2)
        self.assertGreater(len(chunks), 0)
        print(f"  [OK] Grounded RAG retrieved {len(chunks)} chunks successfully")

    def test_07_ml_prediction_tool(self):
        print("\n[TEST 7] Testing Predictive ML Driver Risk Model...")
        res = predict_driver_risk("D101")
        self.assertTrue(res.get("found"))
        self.assertIn(res.get("risk_level"), ["High", "Medium", "Low"])
        self.assertGreaterEqual(res.get("risk_probability"), 0.0)
        self.assertLessEqual(res.get("risk_probability"), 1.0)
        print(f"  [OK] ML Model scored driver D101: {res.get('risk_level')} Risk ({res.get('risk_probability'):.4f})")

    def test_08_langgraph_multi_agent_workflow(self):
        print("\n[TEST 8] Testing LangGraph Multi-Agent Orchestration...")
        time.sleep(5)
        res = run_orchestration("Why is driver D101 underperforming?")
        self.assertIsNotNone(res.get("answer"))
        self.assertIn("route", res)
        print(f"  [OK] LangGraph Orchestrated Route: {res.get('route')}")

    def test_10_entity_aware_data_agent(self):
        print("\n[TEST 10] Testing Entity-Aware Data Agent Routing...")
        res = answer_data_question("What is the rating of driver D101?")
        self.assertIsNotNone(res.get("sql"))
        self.assertIn("D101", res["sql"])
        print("  [OK] Entity-Aware Data Agent Generated Targeted D101 Query")

    def test_11_hitl_approval_workflow(self):
        print("\n[TEST 11] Testing Human-in-the-Loop Pending, Approve, & Reject Workflow...")
        from agentic_ai.memory.persistent_memory import create_pending_action, get_pending_actions, approve_pending_action, reject_pending_action
        
        act_id = create_pending_action("ASSIGN_TRAINING", "D101", "Assigned hospitality coaching")
        self.assertGreater(act_id, 0)
        
        pending_list = get_pending_actions()
        pending_ids = [p["action_id"] for p in pending_list]
        self.assertIn(act_id, pending_ids)
        
        res_app = approve_pending_action(act_id, approved_by="Manager")
        self.assertEqual(res_app["status"], "APPROVED")

        act_id2 = create_pending_action("ASSIGN_TRAINING", "D102", "Assigned hospitality coaching")
        res_rej = reject_pending_action(act_id2, rejection_reason="Already trained", rejected_by="Manager")
        self.assertEqual(res_rej["status"], "REJECTED")

        print("  [OK] HITL Approval Workflow Verified (Pending -> Approved / Rejected)")

    def test_12_differentiated_report_agent(self):
        print("\n[TEST 12] Testing Differentiated Executive Reports...")
        from agentic_ai.agents.report_agent import generate_executive_report

        res_exec = generate_executive_report("Executive Performance Report")
        self.assertEqual(res_exec["status"], "SUCCESS")
        
        res_rev = generate_executive_report("Revenue Analysis Report")
        self.assertEqual(res_rev["status"], "SUCCESS")

        res_drv = generate_executive_report("Driver Performance Report")
        self.assertEqual(res_drv["status"], "SUCCESS")

        print("  [OK] Differentiated Report Generation Verified")

    def test_13_demand_forecasting(self):
        print("\n[TEST 13] Testing Mobility Demand Forecasting...")
        from agentic_ai.ml.demand_forecasting import predict_demand
        res = predict_demand(city="Pune", hour=18)
        self.assertTrue(res["success"])
        self.assertGreater(res["predicted_trips"], 0)
        print(f"  [OK] Forecasted {res['predicted_trips']} trips for Pune at 18:00 ({res['demand_level']})")

    def test_14_anomaly_detection(self):
        print("\n[TEST 14] Testing Revenue Anomaly Detection...")
        from agentic_ai.ml.anomaly_detection import detect_revenue_anomalies
        res = detect_revenue_anomalies(threshold_z=1.5)
        self.assertIn("anomaly_detected", res)
        print(f"  [OK] Anomaly Detection Engine analyzed {res.get('total_days_analyzed', 0)} days")

    def test_15_conversation_memory(self):
        print("\n[TEST 15] Testing Session Conversational Memory & Entity Resolution...")
        from agentic_ai.memory.conversation_memory import update_session_memory, resolve_entity_in_question
        update_session_memory(session_id="t_sess", driver_id="D101")
        res_q = resolve_entity_in_question("What is his rating?", session_id="t_sess")
        self.assertIn("D101", res_q)
        print(f"  [OK] Entity Resolution Transformed 'his' -> '{res_q}'")


if __name__ == "__main__":
    unittest.main()
