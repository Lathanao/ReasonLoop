# abilities/text_completion.py

import requests
import json
import os
import logging
from config.settings import get_setting

logger = logging.getLogger(__name__)

def text_completion_ability(prompt: str) -> str:
    """
    Send a prompt to the configured LLM provider and return the response.

    Args:
        prompt: The text prompt to send to the LLM

    Returns:
        The LLM's response as a string
    """
    provider = get_setting("LLM_PROVIDER").lower()

    if provider == "ollama":
        return _ollama_completion(prompt)
    elif provider == "anthropic":
        return _anthropic_completion(prompt)
    elif provider == "openai":
        return _openai_completion(prompt)
    else:
        logger.error(f"Unknown LLM provider: {provider}")
        return f"Error: Unknown LLM provider '{provider}'"

def _ollama_completion(prompt: str) -> str:
    """Handle Ollama completions"""
    api_url = get_setting("OLLAMA_API_URL")
    model = get_setting("OLLAMA_MODEL")

    # Get all the parameters with defaults if not set
    temperature = get_setting("LLM_TEMPERATURE", 0.7)
    max_tokens = get_setting("LLM_MAX_TOKENS", 2048)
    repeat_penalty = get_setting("LLM_REPEAT_PENALTY", 1.1)
    top_p = get_setting("LLM_TOP_P", 0.8)
    seed = get_setting("LLM_SEED", 42)
    num_ctx = get_setting("LLM_NUM_CTX", 2048)

    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "temperature": temperature,
        "num_predict": max_tokens,
        "repeat_penalty": repeat_penalty,
        "top_p": top_p,
        "seed": seed,
        "num_ctx": num_ctx
    }

    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")
    except Exception as e:
        logger.error(f"Ollama API error: {str(e)}")
        return f"Error calling Ollama API: {str(e)}"

def _anthropic_completion(prompt: str) -> str:
    """Handle Anthropic completions"""
    api_url = get_setting("ANTHROPIC_API_URL")
    api_key = get_setting("ANTHROPIC_API_KEY")
    model = get_setting("ANTHROPIC_MODEL")

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }

    # Anthropic requires a system prompt and uses a different message format
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1024,
        "temperature": 0.7
    }

    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()

        # Correctly parse Anthropic's response format
        if "content" in result:
            for content_block in result["content"]:
                if content_block["type"] == "text":
                    return content_block["text"]
        return ""
    except Exception as e:
        logger.error(f"Anthropic API error: {str(e)}")
        return f"Error calling Anthropic API: {str(e)}"

def _openai_completion(prompt: str) -> str:
    """Handle OpenAI completions"""
    api_url = get_setting("OPENAI_API_URL")
    api_key = get_setting("OPENAI_API_KEY")
    model = get_setting("OPENAI_MODEL")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1024
    }

    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return f"Error calling OpenAI API: {str(e)}"