import time
import functools
from typing import Any, Callable, Dict
from app.core.schema import State

PRICING = {
    "prompt": 10.0 / 1_000_000,
    "completion": 30.0 / 1_000_000
}

def track_agent(func: Callable):
    @functools.wraps(func)
    async def wrapper(state: State, *args, **kwargs):
        start_time = time.perf_counter()
        node_name = func.__name__
        
        # 1. Budget & Policy Check
        used_tokens = state.get("used_tokens", 0)
        budget = state.get("context_window_budget", 10000)
        remaining = budget - used_tokens

        if used_tokens > budget:
            print(f"!!! [HALT] Token budget exceeded in {node_name} !!!")
            # CRITICAL: Return the keys your tests are looking for
            return {
                "next_node": "end",
                "agent_outputs": {
                    "policy_violations": ["CONTEXT_OVERFLOW"],
                    "error": "Budget exceeded"
                }
            }

        print(f"🚀 [START] Agent: {node_name}")
        
        try:
            result = await func(state, *args, **kwargs)
            duration = time.perf_counter() - start_time
            
            # 2. Cost Calculation
            # Check for usage in the result or the state
            usage = result.get("usage", {})
            prompt_t = usage.get("prompt_tokens", 0)
            completion_t = usage.get("completion_tokens", 0)
            new_tokens = prompt_t + completion_t
            
            node_cost = (prompt_t * PRICING["prompt"]) + (completion_t * PRICING["completion"])
            
            # 3. State Updates
            # Inject remaining_budget and updated token counts into the return dict
            if "agent_outputs" not in result:
                result["agent_outputs"] = {}
                
            total_used = used_tokens + new_tokens
            result["used_tokens"] = total_used

            result["agent_outputs"]["remaining_budget"] = budget - total_used
            result["remaining_budget"] = budget - total_used
            
            # 4. Logic for Compression Trigger
            # Move the injection INSIDE the if block
            if (total_used / budget) > 0.9:
                result["agent_outputs"]["compression_used"] = True
                result["compression_used"] = True 
                print(f"[WARN] High budget usage! Flagging compression.")
            
            return result
            
        except Exception as e:
            print(f"[FAILURE] {node_name} crashed: {str(e)}")
            raise e
            
    return wrapper