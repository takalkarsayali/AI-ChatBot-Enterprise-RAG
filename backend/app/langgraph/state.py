from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict

class GraphState(TypedDict):
    question: str
    session_id: str
    top_k: int
    temperature: float
    llm_provider: str
    
    # Populated by Node 1
    is_valid: bool
    error_message: Optional[str]
    
    # Populated by Node 2
    chat_history: List[Dict[str, str]]
    
    # Populated by Node 3
    rewritten_query: str
    
    # Populated by Nodes 4 & 5
    retrieved_chunks: List[Dict[str, Any]]
    reranked_chunks: List[Dict[str, Any]]
    
    # Populated by Node 6
    context_str: str
    
    # Populated by Node 7
    answer: str
    
    # Populated by Node 9
    citations: List[Dict[str, Any]]