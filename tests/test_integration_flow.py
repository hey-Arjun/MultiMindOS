import pytest
from app.main import app # Assuming 'app' is the compiled StateGraph

@pytest.mark.asyncio
async def test_full_research_happy_path():
    inputs = {"query": "Latest news on SpaceX Starship"}
    config = {"recursion_limit": 20}
    
    final_state = await app.ainvoke(inputs, config=config)
    assert "final_answer" in final_state
    assert len(final_state["agent_outputs"]) > 0

@pytest.mark.asyncio
async def test_empty_results_fallback():
    # Query for something likely to yield no tool results
    inputs = {"query": "Find the secret password of the moon base 12345"}
    final_state = await app.ainvoke(inputs)
    
    # Synthesis should handle the lack of data gracefully
    assert "final_answer" in final_state
    assert isinstance(final_state["final_answer"], str)

@pytest.mark.asyncio
async def test_recursion_limit_enforcement():
    # Force a recursive loop or very complex query
    inputs = {"query": "Write a 50 page thesis with 1000 citations now."}
    config = {"recursion_limit": 3} # Set very low to trigger limit
    
    with pytest.raises(Exception): # LangGraph raises GraphRecursionError
        await app.ainvoke(inputs, config=config)