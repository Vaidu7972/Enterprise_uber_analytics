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

    def test_09_pdf_report_generator(self):
        print("\n[TEST 9] Testing PDF Report Generation...")
        sample_res = {
            "question": "Test Question",
            "answer": "Test Answer Summary",
            "recommendations": {"primary_recommendation": "Assign Coaching", "approval_required": True},
            "sources": [{"source": "driver_performance_policy.txt", "page": 1}]
        }
        pdf_path = generate_pdf_report(sample_res, filename="test_report.pdf")
        self.assertTrue(Path(pdf_path).exists())
        print(f"  [OK] PDF Report generated at: {pdf_path}")


if __name__ == "__main__":
    unittest.main()
