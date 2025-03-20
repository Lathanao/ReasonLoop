"""
Web scraping ability to extract content from URLs
"""

import logging
import requests
from bs4 import BeautifulSoup
import time
from config.settings import get_setting

logger = logging.getLogger(__name__)

def web_scrape_ability(url: str) -> str:
    """Extract content from a specific URL"""
    logger.debug(f"ABILITY CALLED: web-scrape with URL: {url}")
    start_time = time.time()

    # Extract URL if it's embedded in text
    if not url.startswith('http'):
        import re
        url_match = re.search(r'https?://[^\s]+', url)
        if url_match:
            url = url_match.group(0)
        else:
            return "Error: No valid URL found in the input."

    try:
        # Send request with a user agent to avoid being blocked
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()

        # Extract the main content
        # This is a simple approach - websites vary greatly in structure
        main_content = ""

        # Try to find main content containers
        main_elements = soup.select('main, article, .content, #content, .main, #main')

        if main_elements:
            # Use the first main element found
            main_content = main_elements[0].get_text(separator='\n', strip=True)
        else:
            # Fallback to body content
            main_content = soup.body.get_text(separator='\n', strip=True)

        # Clean up the text
        import re
        # Remove extra whitespace
        main_content = re.sub(r'\n+', '\n', main_content)
        main_content = re.sub(r'\s+', ' ', main_content)

        # Truncate if too long (max ~8000 chars)
        if len(main_content) > 8000:
            main_content = main_content[:8000] + "...\n[Content truncated due to length]"

        # Add metadata
        title = soup.title.string if soup.title else "No title found"
        result = f"Title: {title}\nURL: {url}\n\nContent:\n{main_content}"

        execution_time = time.time() - start_time
        logger.debug(f"Web scrape completed in {execution_time:.2f}s")

        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"Error in web scrape: {str(e)}")
        return f"Error accessing URL: {str(e)}"
    except Exception as e:
        logger.error(f"Error in web scrape: {str(e)}")
        return f"Error scraping content: {str(e)}"

# Register this ability
if __name__ != "__main__":
    from abilities.ability_registry import register_ability
    register_ability("web-scrape2", web_scrape_ability)