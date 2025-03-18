"""
Text completion ability using Ollama
"""

import logging
from langchain_ollama import OllamaLLM
from config.settings import get_setting
import time

logger = logging.getLogger(__name__)

def get_ollama_llm():
    """Initialize and return the Ollama LLM client"""
    try:
        llm = OllamaLLM(
            model=get_setting("LLM_MODEL"),
            temperature=get_setting("LLM_TEMPERATURE"),
            num_ctx=2048,
            num_predict=get_setting("LLM_MAX_TOKENS"),
            repeat_penalty=1.1,
            top_p=0.8,
            seed=42
        )
        logger.debug(f"Initialized Ollama LLM with model: {get_setting('LLM_MODEL')}")
        return llm
    except Exception as e:
        logger.error(f"Error initializing Ollama: {str(e)}")
        raise

def text_completion_ability(prompt: str) -> str:
    """Use Ollama to complete a text task"""
    logger.debug(f"ABILITY CALLED: text-completion with prompt: {prompt[:100]}...")
    start_time = time.time()

    try:
        llm = get_ollama_llm()
        result = llm.invoke(prompt)

        execution_time = time.time() - start_time
        logger.debug(f"Text completion completed in {execution_time:.2f}s")
        logger.debug(f"Result length: {len(result)} chars")

        return result
    except Exception as e:
        logger.error(f"Error in text completion: {str(e)}")
        return f"Error: {str(e)}"

# Register this ability
if __name__ != "__main__":
    from abilities.ability_registry import register_ability
    register_ability("text-completion", text_completion_ability)