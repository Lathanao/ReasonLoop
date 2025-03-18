"""
Web search ability using DuckDuckGo
"""

import logging
import requests
from bs4 import BeautifulSoup
import time
from config.settings import get_setting

logger = logging.getLogger(__name__)

def web_search_ability(query: str) -> str:
    """Search the web for information"""
    logger.debug(f"ABILITY CALLED: web-search with query: {query}")
    start_time = time.time()

    if not get_setting("WEB_SEARCH_ENABLED"):
        return "Web search is disabled in configuration."

    try:
        # Use DuckDuckGo search (doesn't require API key)
        search_url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract search results
        results = []
        for result in soup.select('.result'):
            title_elem = result.select_one('.result__title')
            link_elem = result.select_one('.result__url')
            snippet_elem = result.select_one('.result__snippet')

            if title_elem and link_elem:
                title = title_elem.get_text(strip=True)
                link = link_elem.get('href', '')
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                results.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet
                })

                if len(results) >= get_setting("WEB_SEARCH_RESULTS_COUNT"):
                    break

        # Format results
        formatted_results = ""
        for i, result in enumerate(results, 1):
            formatted_results += f"{i}. {result['title']}\n   URL: {result['link']}\n   {result['snippet']}\n\n"

        if not formatted_results:
            return "No search results found."

        execution_time = time.time() - start_time
        logger.debug(f"Web search completed in {execution_time:.2f}s")
        logger.debug(f"Found {len(results)} results")

        return formatted_results
    except Exception as e:
        logger.error(f"Error in web search: {str(e)}")
        return f"Error performing web search: {str(e)}"

# Register this ability
if __name__ != "__main__":
    from abilities.ability_registry import register_ability
    register_ability("web-search", web_search_ability)