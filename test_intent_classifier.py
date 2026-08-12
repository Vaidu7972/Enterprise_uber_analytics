from agentic_ai.nlp.intent_classifier import (
    classify_question,
)


question = input(
    "Enter your UberOps question: "
)


result = classify_question(question)


print("\n--- CLASSIFICATION RESULT ---")

print("Route:", result.route)
print("Intent:", result.intent)
print("Entity:", result.entity)
print("Metric:", result.metric)
print("Operation:", result.operation)
print("Limit:", result.limit)
print("Time Period:", result.time_period)
print("Location:", result.location)
print("Identifier:", result.identifier)
print("Reason:", result.routing_reason)