from langchain_core.tools import tool
from services.social_media import SocialDistributionService

@tool
def broadcast_to_socials(topic: str, url: str) -> str:
    """
    Broadcasts a newly published article to all configured social media platforms via official APIs.
    Args:
        topic: A catchy title or brief description of the article.
        url: The live, published URL of the article.
    """
    message = f"New Update: {topic}"
    results = SocialDistributionService.broadcast_all(message, url)
    return f"Broadcast results: {results}"
