from app.core.schema import State
from langgraph.graph import StateGraph, END
from app.agents.orchestrator import orchestrator_node
from app.agents.decomposition import decomposition_node
from app.agents.retrieval import retrieval_node
from app.agents.critique import critique_node
from app.agents.synthesis import synthesis_node
from langgraph.checkpoint.memory import MemorySaver

def create_graph():
    workflow = StateGraph(State)
    memory = MemorySaver()

    # add nodes
    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_node("decomposition", decomposition_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("critique", critique_node)
    workflow.add_node("synthesis",synthesis_node)

    # Define Edges
    workflow.set_entry_point("orchestrator")
    # conditional logic for choosing next-node
    workflow.add_conditional_edges(  
        "orchestrator",
        lambda x: x["next_node"],
        {
            "decomposition": "decomposition",
            "retrieval": "retrieval",
            "critique": "critique",
            "synthesis": "synthesis",
            "end": END
        }
    )
    workflow.add_edge("decomposition", "orchestrator")
    workflow.add_edge("retrieval", "orchestrator")
    workflow.add_edge("critique", "orchestrator")
    workflow.add_edge("synthesis", END)

    return workflow.compile(checkpointer=memory)

