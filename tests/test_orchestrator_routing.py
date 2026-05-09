import pytest
from app.agents.orchestrator import orchestrator_node

@pytest.mark.asyncio
async def test_exit_handshake_immediate():
    state = {"final_answer": "The capital is Paris.", "query": "What is the capital?"}
    result = await orchestrator_node(state)
    # Should exit immediately without LLM logic because answer exists
    assert result["next_node"] == "end"

@pytest.mark.asyncio
async def test_critique_enforcement_routing():
    state = {
        "query": "Deep research on AI",
        "agent_outputs": {"search_results": "Found data..."}, # Data exists
        "sub_tasks": [], # Mocking tasks as completed
        "messages": []
    }
    # No 'critique_report' in agent_outputs
    result = await orchestrator_node(state)
    assert result["next_node"] == "critique"

@pytest.mark.asyncio
async def test_memory_shortcut_routing():
    from langchain_core.messages import HumanMessage, AIMessage
    state = {
        "query": "What is my name?",
        "messages": [HumanMessage(content="My name is Arjun"), AIMessage(content="Hello Arjun")],
        "agent_outputs": {}
    }
    result = await orchestrator_node(state)
    # Should recognize it's conversational and go to synthesis
    assert result["next_node"] == "synthesis"