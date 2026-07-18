from langgraph.graph import StateGraph, START, END
from .state import GraphState
from .nodes import (
    input_validation_node,
    conversation_memory_node,
    query_rewriting_node,
    retriever_node,
    reranker_node,
    context_builder_node,
    llm_generation_node,
    source_citation_node,
    response_formatter_node
)

def route_validation(state: dict):
    """Conditional routing based on Node 1 output."""
    if state.get("is_valid"):
        return "conversation_memory"
    return "end"

def compile_workflow():
    workflow = StateGraph(GraphState)

    # 1. Add all 9 Nodes
    workflow.add_node("input_validation", input_validation_node)
    workflow.add_node("conversation_memory", conversation_memory_node)
    workflow.add_node("query_rewriting", query_rewriting_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("reranker", reranker_node)
    workflow.add_node("context_builder", context_builder_node)
    workflow.add_node("llm_generation", llm_generation_node)
    workflow.add_node("source_citation", source_citation_node)
    workflow.add_node("response_formatter", response_formatter_node)

    # 2. Define the Edges
    workflow.add_edge(START, "input_validation")
    
    # Conditional Edge: If invalid, skip to END. If valid, proceed to memory.
    workflow.add_conditional_edges(
        "input_validation",
        route_validation,
        {
            "conversation_memory": "conversation_memory",
            "end": END
        }
    )

    # Linear Flow for the rest of the RAG pipeline
    workflow.add_edge("conversation_memory", "query_rewriting")
    workflow.add_edge("query_rewriting", "retriever")
    workflow.add_edge("retriever", "reranker")
    workflow.add_edge("reranker", "context_builder")
    workflow.add_edge("context_builder", "llm_generation")
    
    # Spec says Citation Generator is Node 9, we run it after LLM generates text
    workflow.add_edge("llm_generation", "source_citation")
    workflow.add_edge("source_citation", "response_formatter")
    workflow.add_edge("response_formatter", END)

    # 3. Compile
    return workflow.compile()