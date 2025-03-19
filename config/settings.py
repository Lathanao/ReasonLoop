# config/settings.py
import os
import json
from pathlib import Path
from typing import Any, Dict, Optional

class Settings:
    """Settings manager for ReasonLoop"""

    # Default settings
    _defaults = {
        # General settings
        "DEFAULT_OBJECTIVE": "Analyze the data and provide insights",
        "PROMPT_TEMPLATE": "default_tasks",
        "MAX_RETRIES": 3,
        "RETRY_DELAY": 2,

        # LLM settings
        "LLM_PROVIDER": "ollama",
        "LLM_MODEL": None,  # Will be set based on provider
        "LLM_API_URL": None,  # Will be set based on provider
        "LLM_TEMPERATURE": 0.7,
        "LLM_MAX_TOKENS": 2048,
        "LLM_REPEAT_PENALTY": 1.1,
        "LLM_TOP_P": 0.8,
        "LLM_SEED": 42,
        "LLM_NUM_CTX": 2048,

        # Provider-specific settings
        "OLLAMA_API_URL": "http://localhost:11434/api/generate",
        "OLLAMA_MODEL": "llama2",

        "ANTHROPIC_API_URL": "https://api.anthropic.com/v1/messages",
        "ANTHROPIC_API_KEY": "",
        "ANTHROPIC_MODEL": "claude-instant-1.2",

        "OPENAI_API_URL": "https://api.openai.com/v1/chat/completions",
        "OPENAI_API_KEY": "",
        "OPENAI_MODEL": "gpt-3.5-turbo",

        # Database settings
        "DB_CONFIG": {
            "host": "localhost",
            "port": 3306,
            "user": "root",
            "password": "",
            "database": "reasonloop"
        },

        # Web search settings
        "WEB SEARCH_ENABLED": True,
        "WEB SEARCH_RESULTS_COUNT": 5
    }

    def __init__(self):
        """Initialize settings from file and environment variables"""
        self._settings = self._defaults.copy()
        self._settings_file = Path("config/settings.json")

        # Load settings from file if it exists
        self._load_from_file()

        # Override with environment variables
        self._load_from_env()

        # Ensure provider-specific settings are set
        self._update_provider_settings()

    def _load_from_file(self) -> None:
        """Load settings from JSON file"""
        if self._settings_file.exists():
            try:
                with open(self._settings_file, "r") as f:
                    file_settings = json.load(f)
                    self._settings.update(file_settings)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading settings from file: {e}")

    def _load_from_env(self) -> None:
        """Load settings from environment variables"""
        for key in self._settings.keys():
            env_value = os.getenv(key)
            if env_value is not None:
                # Convert environment variable to appropriate type
                if isinstance(self._settings[key], bool):
                    self._settings[key] = env_value.lower() in ("true", "1", "yes")
                elif isinstance(self._settings[key], int):
                    try:
                        self._settings[key] = int(env_value)
                    except ValueError:
                        pass
                elif isinstance(self._settings[key], float):
                    try:
                        self._settings[key] = float(env_value)
                    except ValueError:
                        pass
                elif isinstance(self._settings[key], dict):
                    try:
                        self._settings[key] = json.loads(env_value)
                    except json.JSONDecodeError:
                        pass
                else:
                    self._settings[key] = env_value

    def _update_provider_settings(self) -> None:
        """Update LLM_MODEL and LLM_API_URL based on provider"""
        provider = self._settings["LLM_PROVIDER"].lower()

        # Set LLM_API_URL based on provider if not explicitly set
        if not self._settings["LLM_API_URL"]:
            provider_url_key = f"{provider.upper()}_API_URL"
            self._settings["LLM_API_URL"] = self._settings.get(provider_url_key)

        # Set LLM_MODEL based on provider if not explicitly set
        if not self._settings["LLM_MODEL"]:
            provider_model_key = f"{provider.upper()}_MODEL"
            self._settings["LLM_MODEL"] = self._settings.get(provider_model_key)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting by key"""
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a setting by key"""
        self._settings[key] = value

        # If changing provider, update related settings
        if key == "LLM_PROVIDER":
            self._update_provider_settings()

    def save(self) -> Path:
        """Save settings to file"""
        # Create config directory if it doesn't exist
        self._settings_file.parent.mkdir(exist_ok=True)

        # Convert any non-serializable values to strings
        serializable_settings = {}
        for key, value in self._settings.items():
            if isinstance(value, (str, int, float, bool, list)) or value is None:
                serializable_settings[key] = value
            elif isinstance(value, dict):
                # Handle dictionaries by checking if they're serializable
                try:
                    json.dumps(value)
                    serializable_settings[key] = value
                except TypeError:
                    serializable_settings[key] = str(value)
            else:
                serializable_settings[key] = str(value)

        # Save to file
        with open(self._settings_file, "w") as f:
            json.dump(serializable_settings, f, indent=2)

        return self._settings_file

    def get_all(self) -> Dict[str, Any]:
        """Get all settings"""
        return self._settings.copy()


# Create a singleton instance
_settings = Settings()

# Public API
def get_setting(key: str, default: Any = None) -> Any:
    """Get a setting by key"""
    return _settings.get(key, default)

def update_setting(key: str, value: Any) -> None:
    """Update a setting by key"""
    _settings.set(key, value)

def save_settings() -> Path:
    """Save settings to file"""
    return _settings.save()

def get_all_settings() -> Dict[str, Any]:
    """Get all settings"""
    return _settings.get_all()