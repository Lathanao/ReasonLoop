# utils/llm_utils.py

import requests
import json
import time
import logging
from config.settings import get_setting

logger = logging.getLogger(__name__)

def test_llm_service():
    """Test if the LLM service is available and responding correctly

    Returns:
        tuple: (bool, str) - (success, message)
    """
    provider = get_setting("LLM_PROVIDER").lower()

    if provider == "ollama":
        return _test_ollama()
    elif provider == "anthropic":
        return _test_anthropic()
    elif provider == "openai":
        return _test_openai()
    else:
        return False, f"Unknown LLM provider: {provider}"

def _test_ollama():
    """Test Ollama service"""
    api_url = get_setting("OLLAMA_API_URL")
    model = get_setting("OLLAMA_MODEL")

    # Get parameters with defaults
    temperature = get_setting("LLM_TEMPERATURE", 0.7)
    max_tokens = 10  # Small for testing
    repeat_penalty = get_setting("LLM_REPEAT_PENALTY", 1.1)
    top_p = get_setting("LLM_TOP_P", 0.8)
    seed = get_setting("LLM_SEED", 42)
    num_ctx = get_setting("LLM_NUM_CTX", 2048)

    logger.info(f"Testing Ollama service at {api_url} with model {model}")

    test_prompt = "Respond with 'OK' if you can read this message."

    try:
        headers = {"Content-Type": "application/json"}
        data = {
            "model": model,
            "prompt": test_prompt,
            "stream": False,
            "temperature": temperature,
            "num_predict": max_tokens,
            "repeat_penalty": repeat_penalty,
            "top_p": top_p,
            "seed": seed,
            "num_ctx": num_ctx
        }

        start_time = time.time()
        response = requests.post(api_url, headers=headers, json=data, timeout=10)
        response_time = time.time() - start_time

        if response.status_code != 200:
            return False, f"Ollama service returned status code {response.status_code}"

        try:
            result = response.json()
            if "response" in result:
                logger.info(f"Ollama test successful. Response time: {response_time:.2f}s")
                return True, f"Ollama service is available. Response time: {response_time:.2f}s"
            else:
                return False, f"Unexpected response format: {result}"
        except json.JSONDecodeError:
            return False, "Failed to parse JSON response from Ollama"

    except requests.exceptions.ConnectionError:
        return False, "Failed to connect to Ollama service. Check if Ollama is running."
    except requests.exceptions.Timeout:
        return False, "Connection to Ollama service timed out."
    except Exception as e:
        return False, f"Error testing Ollama service: {str(e)}"

def _test_anthropic():
    """Test Anthropic service"""
    api_url = get_setting("ANTHROPIC_API_URL")
    api_key = get_setting("ANTHROPIC_API_KEY")
    model = get_setting("ANTHROPIC_MODEL")

    if not api_key:
        return False, "Anthropic API key is not set"

    logger.info(f"Testing Anthropic service with model {model}")

    test_prompt = "Respond with 'OK' if you can read this message."

    try:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }

        data = {
            "model": model,
            "messages": [{"role": "user", "content": test_prompt}],
            "max_tokens": 10,
            "temperature": 0.7
        }

        start_time = time.time()
        response = requests.post(api_url, headers=headers, json=data, timeout=10)
        response_time = time.time() - start_time

        if response.status_code != 200:
            return False, f"Anthropic service returned status code {response.status_code}"

        try:
            result = response.json()
            # Check for content blocks in the response
            if "content" in result:
                logger.info(f"Anthropic test successful. Response time: {response_time:.2f}s")
                return True, f"Anthropic service is available. Response time: {response_time:.2f}s"
            else:
                return False, f"Unexpected response format: {result}"
        except json.JSONDecodeError:
            return False, "Failed to parse JSON response from Anthropic"

    except requests.exceptions.ConnectionError:
        return False, "Failed to connect to Anthropic service."
    except requests.exceptions.Timeout:
        return False, "Connection to Anthropic service timed out."
    except Exception as e:
        return False, f"Error testing Anthropic service: {str(e)}"

    """Test Anthropic service"""
    api_url = get_setting("ANTHROPIC_API_URL")
    api_key = get_setting("ANTHROPIC_API_KEY")
    model = get_setting("ANTHROPIC_MODEL")

    if not api_key:
        return False, "Anthropic API key is not set"

    logger.info(f"Testing Anthropic service with model {model}")

    test_prompt = "Respond with 'OK' if you can read this message."

    try:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }

        data = {
            "model": model,
            "messages": [{"role": "user", "content": test_prompt}],
            "max_tokens": 10
        }

        start_time = time.time()
        response = requests.post(api_url, headers=headers, json=data, timeout=10)
        response_time = time.time() - start_time

        if response.status_code != 200:
            return False, f"Anthropic service returned status code {response.status_code}"

        try:
            result = response.json()
            if "content" in result:
                logger.info(f"Anthropic test successful. Response time: {response_time:.2f}s")
                return True, f"Anthropic service is available. Response time: {response_time:.2f}s"
            else:
                return False, f"Unexpected response format: {result}"
        except json.JSONDecodeError:
            return False, "Failed to parse JSON response from Anthropic"

    except requests.exceptions.ConnectionError:
        return False, "Failed to connect to Anthropic service."
    except requests.exceptions.Timeout:
        return False, "Connection to Anthropic service timed out."
    except Exception as e:
        return False, f"Error testing Anthropic service: {str(e)}"

def _test_openai():
    """Test OpenAI service"""
    api_url = get_setting("OPENAI_API_URL")
    api_key = get_setting("OPENAI_API_KEY")
    model = get_setting("OPENAI_MODEL")

    if not api_key:
        return False, "OpenAI API key is not set"

    logger.info(f"Testing OpenAI service with model {model}")

    test_prompt = "Respond with 'OK' if you can read this message."

    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        data = {
            "model": model,
            "messages": [{"role": "user", "content": test_prompt}],
            "temperature": 0.7,
            "max_tokens": 10
        }

        start_time = time.time()
        response = requests.post(api_url, headers=headers, json=data, timeout=10)
        response_time = time.time() - start_time

        if response.status_code != 200:
            return False, f"OpenAI service returned status code {response.status_code}"

        try:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                logger.info(f"OpenAI test successful. Response time: {response_time:.2f}s")
                return True, f"OpenAI service is available. Response time: {response_time:.2f}s"
            else:
                return False, f"Unexpected response format: {result}"
        except json.JSONDecodeError:
            return False, "Failed to parse JSON response from OpenAI"

    except requests.exceptions.ConnectionError:
        return False, "Failed to connect to OpenAI service."
    except requests.exceptions.Timeout:
        return False, "Connection to OpenAI service timed out."
    except Exception as e:
        return False, f"Error testing OpenAI service: {str(e)}"