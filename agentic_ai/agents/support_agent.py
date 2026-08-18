from google.genai import types    #config file 

from agentic_ai.config.agent_config import (
    GEMINI_MODEL,
)

from agentic_ai.llm.gemini_client import (
    client,
)

from agentic_ai.prompts.support_agent_prompt import (
    SUPPORT_AGENT_PROMPT,
)

from agentic_ai.rag.vector_store import (
    search_support_docs,
)


def build_context(           #llm context   source info for gemini
    retrieved_chunks: list[dict]
) -> str:

    context_parts = []

    for index, chunk in enumerate(
        retrieved_chunks,
        start=1
    ):

        context_parts.append(
            f"""
DOCUMENT {index}

Source: {chunk["source"]}
Page: {chunk["page"]}
Chunk: {chunk["chunk_number"]}

Content:
{chunk["text"]}
"""
        )

    return "\n".join(
        context_parts
    )


def build_sources(
    retrieved_chunks: list[dict]
) -> list[dict]:

    sources = []

    seen = set()

    for chunk in retrieved_chunks:

        source_key = (
            chunk["source"],
            chunk["page"]
        )

        if source_key in seen:
            continue

        seen.add(
            source_key
        )

        sources.append(         #adding sturctured source
            {
                "source": chunk["source"],
                "page": chunk["page"],
            }
        )

    return sources


def answer_support_question(
    question: str,
    top_k: int = 4
) -> dict:

    # -----------------------------------------
    # STEP 1: RETRIEVE RELEVANT DOCUMENTS
    # -----------------------------------------

    retrieved_chunks = search_support_docs(
        question,
        top_k=top_k
    )

    # -----------------------------------------
    # STEP 2: BUILD RAG CONTEXT
    # -----------------------------------------

    context = build_context(
        retrieved_chunks
    )

    # -----------------------------------------
    # STEP 3: CREATE AUGMENTED PROMPT
    # -----------------------------------------

    prompt = f"""
USER QUESTION:

{question}


RETRIEVED SUPPORT CONTEXT:

{context}


Using only the retrieved support context above,
answer the user's question.
"""

    # -----------------------------------------
    # STEP 4: ASK GEMINI
    # -----------------------------------------

    from agentic_ai.llm.gemini_client import safe_generate_content

    response = safe_generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SUPPORT_AGENT_PROMPT
        ),
    )

    # -----------------------------------------
    # STEP 5: BUILD SOURCES & ANSWER
    # -----------------------------------------

    sources = build_sources(
        retrieved_chunks
    )

    if response and hasattr(response, "text") and response.text:    #check gemini response 
        answer_text = response.text
    else:
        # Grounded fallback: return top retrieved text chunk directly
        top_text = retrieved_chunks[0]["text"] if retrieved_chunks else "No support documents found."
        answer_text = f"**Grounded Support Policy Extract:**\n\n{top_text}"

    # -----------------------------------------
    # STEP 6: RETURN STANDARD RESULT
    # -----------------------------------------

    return {
        "answer": answer_text,
        "sources": sources,
        "retrieved_chunks":
            retrieved_chunks,
    }

# user --> accident ? ---> vector store.py --->
#  chromdb (check similar value in ur vectore db where source data chunk  )---> 
# similar chunk --> ans ---?  gemini summarise 
# RAG -- source data --> documentloader.py read --> chunker --> chunks  (source page chunk no )
#embedding (text to vector) --> embeding service.py --> gemini model use 789vector  
#vectordb -->chromDB  check which vector close to ur question to ur source  
#vectorstore.py -->s 70% meaning 30 % exact word mhnjy accurate 