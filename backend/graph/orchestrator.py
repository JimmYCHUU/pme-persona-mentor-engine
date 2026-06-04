"""Graph orchestrator — builds and compiles the LangGraph pipeline.

Graph order is fixed forever (ARCH-3):
    memory → etm → socratic → persona → guardian → END

mastery_node and cert_node are NEVER in the graph (ARCH-2).
They run as FastAPI BackgroundTasks only.
"""
from langgraph.graph import StateGraph, END
from graph.state import PMEState
from graph.nodes.memory_node   import memory_node
from graph.nodes.etm_node      import etm_node
from graph.nodes.socratic_node import socratic_node
from graph.nodes.persona_node  import persona_node
from graph.nodes.guardian_node import guardian_node


def build_graph():
    g = StateGraph(PMEState)
    g.add_node("memory",   memory_node)
    g.add_node("etm",      etm_node)
    g.add_node("socratic", socratic_node)
    g.add_node("persona",  persona_node)
    g.add_node("guardian", guardian_node)
    g.set_entry_point("memory")
    g.add_edge("memory",   "etm")
    g.add_edge("etm",      "socratic")
    g.add_edge("socratic", "persona")
    g.add_edge("persona",  "guardian")
    g.add_edge("guardian", END)
    return g.compile()


pme_graph = build_graph()
