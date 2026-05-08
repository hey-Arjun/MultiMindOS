import time
import functools
from typing import Any, Callable
from app.core.schema import State

def track_agent(func: Callable):
    """
    Telemetry decorator to log agent performance and health.
    """
    @functools.wraps(func)
    async def wrapper(state: State, *args, **kwargs):
        start_time = time.perf_counter()
        node_name = func.__name__
        
        # 1. Budget Check
        if state.get("used_tokens", 0) > state.get("context_window_budget", 4000):
            print(f"!!! [HALT] Token budget exceeded in {node_name} !!!")
            return {"next_node": "end", "final_answer": "Error: AI budget exceeded."}

        print(f"🚀 [START] Agent: {node_name}")
        
        try:
            result = await func(state, *args, **kwargs)
            duration = time.perf_counter() - start_time
            
            # 2. Log success
            print(f"✅ [SUCCESS] {node_name} finished in {duration:.2f}s")
            return result
            
        except Exception as e:
            print(f"❌ [FAILURE] {node_name} crashed: {str(e)}")
            raise e
            
    return wrapper