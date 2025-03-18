from abilities.text_completion import text_completion_ability
from abilities.web_search import web_search_ability
from abilities.web_scrape import web_scrape_ability
# Import other abilities

from abilities.ability_registry import register_ability

# Register all abilities
register_ability("text-completion", text_completion_ability)
register_ability("web-search", web_search_ability)
register_ability("web_scrape", web_scrape_ability)