from langchain_core.tools import tool
from services.hacker_news import HackerNewsService
from services.rss_reader import RSSNewsService

@tool
def get_trending_tech_news() -> str:
    """
    Fetch the top 3 trending tech news articles from Hacker News right now.
    Returns a string containing the titles and URLs of the news.
    """
    try:
        story_ids = HackerNewsService.fetch_top_stories(3)
        
        news_summaries = []
        for i, story_id in enumerate(story_ids):
            story = HackerNewsService.fetch_story_details(story_id)
            title = story.get('title', 'Unknown Title')
            url = story.get('url', f"https://news.ycombinator.com/item?id={story_id}")
            news_summaries.append(f"{i+1}. {title}\nSource: {url}")
            
        return "Latest Trending Tech News:\n" + "\n\n".join(news_summaries)
    except Exception as e:
        return f"Error fetching news (failed permanently after retries): {str(e)}"

@tool
def get_global_news(category: str) -> str:
    """
    Fetch the latest headlines from major media outlets.
    Valid categories are 'ethiopia', 'africa', or 'global'. 
    Use 'ethiopia' for local Horn of Africa news (ENA, Addis Fortune, Addis Standard).
    """
    return RSSNewsService.get_news_by_category(category)
