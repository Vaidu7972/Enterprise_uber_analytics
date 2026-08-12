from agentic_ai.llm.gemini_client import ask_gemini


question = "Explain data engineering in 3 simple lines."

answer = ask_gemini(question)

print("Question:")
print(question)

print("\nGemini Response:")
print(answer)