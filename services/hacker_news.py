import requests
from tenacity import retry, stop_after_attempt, wait_exponential

class HackerNewsService:
    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def fetch_top_stories(limit=3):
        top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        response = requests.get(top_stories_url, timeout=10)
        response.raise_for_status()
        return response.json()[:limit]

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def fetch_story_details(story_id):
        story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        response = requests.get(story_url, timeout=10)
        response.raise_for_status()
        return response.json()
