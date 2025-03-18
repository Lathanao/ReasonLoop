"""
Prompt logging system to track all prompts and responses
"""

import logging
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Configure prompt logging
PROMPT_LOG_ENABLED = os.getenv("REASONLOOP_PROMPT_LOG_ENABLED", "true").lower() == "true"
PROMPT_LOG_DIR = os.getenv("REASONLOOP_PROMPT_LOG_DIR", "logs/prompts")
PROMPT_LOG_LEVEL = os.getenv("REASONLOOP_PROMPT_LOG_LEVEL", "DEBUG")

# Create prompt log directory if it doesn't exist
if PROMPT_LOG_ENABLED and not os.path.exists(PROMPT_LOG_DIR):
    os.makedirs(PROMPT_LOG_DIR, exist_ok=True)

def log_prompt(
    prompt: str,
    response: str,
    template_name: Optional[str] = None,
    ability: Optional[str] = None,
    task_id: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log a prompt and its response with metadata
    """
    if not PROMPT_LOG_ENABLED:
        return

    # Create a log entry
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "template_name": template_name,
        "ability": ability,
        "task_id": task_id,
        "prompt": prompt,
        "response": response,
        "metadata": metadata or {}
    }

    # Log to the application log
    log_level = getattr(logging, PROMPT_LOG_LEVEL)
    logger.log(log_level, f"PROMPT: {prompt[:100]}... → RESPONSE: {response[:100]}...")

    # Write to prompt log file
    try:
        # Create a unique filename
        date_str = datetime.now().strftime("%Y%m%d")
        time_str = datetime.now().strftime("%H%M%S")
        task_str = f"task{task_id}_" if task_id is not None else ""
        ability_str = f"{ability}_" if ability else ""
        template_str = f"{template_name}_" if template_name else ""

        filename = f"{date_str}_{time_str}_{template_str}{ability_str}{task_str}prompt.json"
        filepath = os.path.join(PROMPT_LOG_DIR, filename)

        with open(filepath, 'w') as f:
            json.dump(log_entry, f, indent=2)

    except Exception as e:
        logger.error(f"Error writing prompt log: {str(e)}")