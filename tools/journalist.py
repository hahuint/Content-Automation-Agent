from langchain_core.tools import tool
from services.journalist import JournalistService
from tools.wordpress import publish_to_wordpress

import json

@tool
def delegate_to_journalist(topic: str, raw_facts: str) -> str:
    """
    Hands off the research to the AI Journalist to write a professional HTML blog post, and AUTOMATICALLY publishes it to WordPress.
    Args:
        topic: The general topic you found
        raw_facts: The raw news text you fetched
    """
    # 1. The Journalist generates the perfect JSON payload
    result_str = JournalistService.write_article(topic, raw_facts)
    
    if "❌ Error" in result_str:
        return result_str
        
    try:
        data = json.loads(result_str)
        
        # 2. Directly publish to WordPress (Bypassing Llama so no characters are ever lost)
        return publish_to_wordpress.invoke({
            "title": data["title"],
            "content": data["content"],
            "image_search_term": data["image_search_term"],
            "comma_separated_tags": data["tags"],
            "seo_meta_description": data["seo_meta_description"]
        })
    except json.JSONDecodeError as e:
        return f"❌ Error: Grok failed to return valid JSON. ({e}) Raw Output: {result_str}"
