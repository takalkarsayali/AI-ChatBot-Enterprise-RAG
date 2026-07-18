import json
from app.services.memory_service import memory_manager
from app.llm.factory import get_llm_client

async def input_validation_node(state: dict):
    """Node 1: Validates the incoming query."""
    question = state.get("question", "").strip()
    is_valid = bool(question and len(question) > 2)
    return {"is_valid": is_valid, "error_message": None if is_valid else "Query too short."}

async def conversation_memory_node(state: dict):
    """Node 2: Loads short-term memory from SQLite."""
    session_id = state.get("session_id", "default")
    chat_history = memory_manager.get_history(session_id)
    return {"chat_history": chat_history}

async def query_rewriting_node(state: dict):
    """Node 3: Rewrites query based on chat history (Mocked for testing)."""
    return {"rewritten_query": state.get("question")}

async def retriever_node(state: dict):
    """Node 4: Retrieves chunks from Pinecone."""
    query = state.get("rewritten_query")
    top_k = state.get("top_k", 5)
    
    # MOCK chunks for testing the graph flow. 
    mock_chunks = [
        {"chunk_id": "chunk-123", "text": "AI agents are autonomous systems.", "document_name": "ai_basics.pdf", "page_number": 1, "relevance_score": 0.95}
    ]
    return {"retrieved_chunks": mock_chunks}

async def reranker_node(state: dict):
    """Node 5: Reranks the retrieved chunks."""
    return {"reranked_chunks": state.get("retrieved_chunks", [])}

async def context_builder_node(state: dict):
    """Node 6: Formats chunks into a single context string."""
    chunks = state.get("reranked_chunks", [])
    context_str = "\n\n".join([f"Source ({c.get('document_name')}): {c.get('text')}" for c in chunks])
    return {"context_str": context_str}

async def llm_generation_node(state: dict):
    """Node 7: Generates the final answer using the dynamic LLM provider."""
    provider = state.get("llm_provider", "gemini")
    temperature = state.get("temperature", 0.3)
    query = state.get("rewritten_query")
    context = state.get("context_str")
    history = state.get("chat_history", [])
    
    prompt = f"Context:\n{context}\n\nQuestion:\n{query}\n\nAnswer concisely based on the context."
    
    try:
        llm = get_llm_client(provider)
        answer = llm.generate(prompt, temperature=temperature)
    except Exception as e:
        answer = f"Error generating response: {str(e)}"
        
    return {"answer": answer}

async def source_citation_node(state: dict):
    """Node 9: Extracts and formats citations."""
    chunks = state.get("reranked_chunks", [])
    citations = []
    for c in chunks:
        citations.append({
            "document_name": c.get("document_name", "Unknown"),
            "page_number": c.get("page_number", 0),
            "section": c.get("section", "General"),
            "chunk_id": c.get("chunk_id", "Unknown"),
            "relevance_score": c.get("relevance_score", 0.0)
        })
    return {"citations": citations}

async def response_formatter_node(state: dict):
    """Node 8: Saves to memory before concluding."""
    session_id = state.get("session_id", "default")
    question = state.get("question")
    answer = state.get("answer")
    
    if session_id and question and answer and not answer.startswith("Error"):
        memory_manager.add_exchange(session_id, question, answer)
        
    return state