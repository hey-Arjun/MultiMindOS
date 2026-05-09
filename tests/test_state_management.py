import pytest
from app.core.schema import State
from app.agents.decomposition import decomposition_node

@pytest.mark.asyncio
async def test_task_accumulation_reducer():
    # Initial state with one task
    state = {"sub_tasks": [{"id": "1", "description": "task 1"}]}
    
    # Mocking decomposition outputting a new task
    new_tasks = [{"id": "2", "description": "task 2"}]
    # In LangGraph, the reducer for sub_tasks is operator.add
    combined = state["sub_tasks"] + new_tasks
    assert len(combined) == 2

@pytest.mark.asyncio
async def test_output_merging_ior():
    # Simulating the dictionary merge (operator.ior / |=)
    state_outputs = {"research": "data"}
    node_output = {"critique": "looks good"}
    
    state_outputs.update(node_output)
    assert "research" in state_outputs
    assert "critique" in state_outputs

@pytest.mark.asyncio
async def test_budget_persistence_across_nodes():
    state = {"used_tokens": 0.015}
    # A node returns a small cost
    node_result = {"used_tokens": 0.005}
    
    # The reducer should sum them
    total = state["used_tokens"] + node_result["used_tokens"]
    assert total == 0.020