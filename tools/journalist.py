from langchain_core.tools import tool
from services.journalist import JournalistService
from tools.wordpress import publish_to_wordpress

import json

@tool
def delegate_to_journalist(topic: str, raw_facts: str) -> str:
    """
    Hands off the research to the AI Journalist to compose a professional, SEO-optimized HTML article.
    Returns the composed article as a JSON string (title, content, tags, image_search_term).
    Args:
        topic: The general topic you found
        raw_facts: The raw news text you fetched
    """
    # Compose the content (Delegates to Grok/High-power model)
    return JournalistService.write_article(topic, raw_facts)

