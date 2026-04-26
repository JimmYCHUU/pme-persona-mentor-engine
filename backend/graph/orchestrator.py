"""LangGraph orchestrator wiring for the PME pipeline."""

from langgraph.graph import END, StateGraph

from graph.nodes.etm_node import etm_node
from graph.nodes.guardian_node import guardian_node
from graph.nodes.memory_node import memory_node
from graph.nodes.persona_node import persona_node
from graph.nodes.socratic_node import socratic_node
from graph.state import PMEState


def build_graph() -> StateGraph:
    """Build and compile the graph in fixed node order."""

    graph = StateGraph(PMEState)
    graph.add_node("memory", memory_node)
    graph.add_node("etm", etm_node)
    graph.add_node("socratic", socratic_node)
    graph.add_node("persona", persona_node)
    graph.add_node("guardian", guardian_node)

    graph.set_entry_point("memory")
    graph.add_edge("memory", "etm")
    graph.add_edge("etm", "socratic")
    graph.add_edge("socratic", "persona")
    graph.add_edge("persona", "guardian")
    graph.add_edge("guardian", END)
    return graph.compile()


pme_graph = build_graph()
