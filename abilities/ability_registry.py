"""
Registry of all available abilities
"""
import logging
import time
from typing import Dict, Callable, Any, Optional

logger = logging.getLogger(__name__)

# Dictionary to store all registered abilities
ABILITY_REGISTRY: Dict[str, Callable] = {}

def register_ability(name: str, func: Callable) -> None:
    """Register an ability function with a name"""
    logger.debug(f"Registering ability: {name}")
    ABILITY_REGISTRY[name] = func

def get_ability(name: str) -> Optional[Callable]:
    """Get an ability function by name"""
    ability = ABILITY_REGISTRY.get(name)
    if ability is None:
        logger.warning(f"Ability not found: {name}")
    return ability

def list_abilities() -> Dict[str, Callable]:
    """List all registered abilities"""
    return ABILITY_REGISTRY.copy()

def execute_ability(name: str, *args: Any, **kwargs: Any) -> Any:
    """Execute an ability by name with arguments"""
    from utils.prompt_logger import log_prompt

    ability = get_ability(name)
    if ability is None:
        logger.warning(f"Ability not found: {name}")
        raise ValueError(f"Ability not found: {name}")

    logger.debug(f"Executing ability: {name}")

    # Extract task_id from kwargs if present
    task_id = kwargs.pop("task_id", None)

    # Get the prompt (usually the first argument for text abilities)
    prompt = args[0] if args and isinstance(args[0], str) else str(args)

    # Execute the ability and capture the response
    start_time = time.time()
    try:
        response = ability(*args, **kwargs)
        execution_time = time.time() - start_time

        # Log the prompt and response
        log_prompt(
            prompt=prompt,
            response=response if isinstance(response, str) else str(response),
            ability=name,
            task_id=task_id,
            metadata={
                "execution_time": execution_time,
                "args": str(args[1:]) if len(args) > 1 else None,
                "kwargs": str(kwargs) if kwargs else None
            }
        )

        return response
    except Exception as e:
        execution_time = time.time() - start_time

        # Log the error
        log_prompt(
            prompt=prompt,
            response=f"ERROR: {str(e)}",
            ability=name,
            task_id=task_id,
            metadata={
                "execution_time": execution_time,
                "error": str(e),
                "args": str(args[1:]) if len(args) > 1 else None,
                "kwargs": str(kwargs) if kwargs else None
            }
        )
        raise
    