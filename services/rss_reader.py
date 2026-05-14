import feedparser
from tenacity import retry, stop_after_attempt, wait_exponential

class RSSNewsService:
    # Dictionary of categorized news feeds
    FEEDS = {
        "ethiopia": [
            {"name": "Ethiopian News Agency (ENA)", "url": "https://news.google.com/rss/search?q=site:ena.et+OR+site:ena.gov.et"},
            {"name": "Addis Fortune", "url": "https://addisfortune.news/feed/"},
            {"name": "Addis Standard", "url": "https://addisstandard.com/feed/"},
            {"name": "The Ethiopian Tribune", "url": "https://news.google.com/rss/search?q=site:ethiotribune.com"},
            {"name": "African Business (Ethiopia)", "url": "https://news.google.com/rss/search?q=Ethiopia+site:african.business"}
        ],
        "africa": [
            {"name": "Addis Standard", "url": "https://addisstandard.com/feed/"},
            {"name": "Al Jazeera Africa", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
            {"name": "DW Africa", "url": "https://rss.dw.com/xml/rss-en-africa"},
            {"name": "France 24 Africa", "url": "https://www.france24.com/en/africa/rss"},
            {"name": "BBC Africa", "url": "http://feeds.bbci.co.uk/news/world/africa/rss.xml"}
        ],
        "global": [
            {"name": "Reuters World", "url": "https://news.google.com/rss/search?q=when:24h+topic:world"},
            {"name": "Al Jazeera Global", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
            {"name": "BBC World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
            {"name": "CNN World", "url": "http://rss.cnn.com/rss/edition_world.rss"}
        ],
        "trending": [
            {"name": "Google News Breaking", "url": "https://news.google.com/rss/search?q=when:24h+breaking+news"},
            {"name": "TechCrunch Trending", "url": "https://techcrunch.com/feed/"},
            {"name": "Reuters Latest", "url": "https://news.google.com/rss/search?q=when:24h+site:reuters.com"}
        ]
    }

    @staticmethod
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=5))
    def fetch_feed(url: str, limit: int = 15):
        """Fetches and parses an RSS XML feed"""
        parsed = feedparser.parse(url)
        results = []
        for entry in parsed.entries[:limit]:
            results.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", "")
            })
        return results

    @staticmethod
    def get_news_by_category(category: str = "africa"):
        """Aggregates news from all outlets in a specific category"""
        category = category.lower()
        
        # Map 'world' to 'global' if requested
        lookup_key = "global" if category == "world" else category
        feeds = RSSNewsService.FEEDS.get(lookup_key, RSSNewsService.FEEDS["global"])
        
        all_news = []
        all_news.append(f"🌍 === LATEST {category.upper()} NEWS HEADLINES ===")
        
        for feed in feeds:
            try:
                entries = RSSNewsService.fetch_feed(feed["url"], limit=15)
                for entry in entries:
                    all_news.append(f"[{feed['name']}] {entry['title']}\nLink: {entry['link']}")
            except Exception as e:
                print(f"Failed to fetch {feed['name']}: {e}")
                
        return "\n\n".join(all_news)
