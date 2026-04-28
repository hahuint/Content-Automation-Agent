import pytest
import responses
from services.rss_reader import RSSNewsService

# Sample RSS XML to mock the response
MOCK_RSS_XML = """<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>Mock News Feed</title>
  <item>
    <title>Test Ethiopian News Headline</title>
    <link>https://example.com/news1</link>
  </item>
  <item>
    <title>Another Great Tech Story</title>
    <link>https://example.com/news2</link>
  </item>
</channel>
</rss>
"""

from unittest.mock import patch

@patch('services.rss_reader.feedparser.parse')
def test_fetch_feed(mock_parse):
    # Setup mock return value
    class MockEntry:
        def get(self, key, default=""):
            if key == "title": return "Test Ethiopian News Headline"
            if key == "link": return "https://example.com/news1"
            return default

    class MockParsed:
        entries = [MockEntry(), MockEntry()]

    mock_parse.return_value = MockParsed()

    # Call the service
    test_url = "https://mocknews.com/feed"
    entries = RSSNewsService.fetch_feed(test_url, limit=2)

    # Assertions
    assert len(entries) == 2
    assert entries[0]['title'] == "Test Ethiopian News Headline"
    assert entries[0]['link'] == "https://example.com/news1"
