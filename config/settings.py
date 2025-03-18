"""
Configuration settings for the application
"""

import os
from typing import Dict, Any

# Default objective
DEFAULT_OBJECTIVE = "Create a 3-day itinerary for Bangkok"

# LLM configuration
LLM_MODEL = os.getenv("REASONLOOP_LLM_MODEL", "llama3.2")
LLM_TEMPERATURE = float(os.getenv("REASONLOOP_LLM_TEMPERATURE", "0.1"))
LLM_MAX_TOKENS = int(os.getenv("REASONLOOP_LLM_MAX_TOKENS", "2048"))

# Database configuration
DB_CONFIG = {
    "host": os.getenv("REASONLOOP_DB_HOST", "localhost"),
    "user": os.getenv("REASONLOOP_DB_USER", "root"),
    "password": os.getenv("REASONLOOP_DB_PASSWORD", ""),
    "database": os.getenv("REASONLOOP_DB_NAME", "your_database")
}

# Web search configuration
WEB_SEARCH_ENABLED = os.getenv("REASONLOOP_WEB_SEARCH_ENABLED", "true").lower() == "true"
WEB_SEARCH_RESULTS_COUNT = int(os.getenv("REASONLOOP_WEB_SEARCH_RESULTS", "5"))

# Execution configuration
MAX_RETRIES = int(os.getenv("REASONLOOP_MAX_RETRIES", "2"))
RETRY_DELAY = float(os.getenv("REASONLOOP_RETRY_DELAY", "2.0"))

# Store all settings in a dictionary for easy access
SETTINGS = {
    "DEFAULT_OBJECTIVE": DEFAULT_OBJECTIVE,
    "LLM_MODEL": LLM_MODEL,
    "LLM_TEMPERATURE": LLM_TEMPERATURE,
    "LLM_MAX_TOKENS": LLM_MAX_TOKENS,
    "DB_CONFIG": DB_CONFIG,
    "WEB_SEARCH_ENABLED": WEB_SEARCH_ENABLED,
    "WEB_SEARCH_RESULTS_COUNT": WEB_SEARCH_RESULTS_COUNT,
    "MAX_RETRIES": MAX_RETRIES,
    "RETRY_DELAY": RETRY_DELAY
}

def get_setting(key: str, default: Any = None) -> Any:
    """Get a setting by key"""
    return SETTINGS.get(key, default)

def update_setting(key: str, value: Any) -> None:
    """Update a setting"""
    SETTINGS[key] = value

    # Also update the module-level variable if it exists
    if key in globals():
        globals()[key] = value