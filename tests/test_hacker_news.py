import responses
from services.hacker_news import HackerNewsService

@responses.activate
def test_fetch_top_stories_success():
    # Arrange: Mock the API response
    responses.add(
        responses.GET,
        "https://hacker-news.firebaseio.com/v0/topstories.json",
        json=[101, 102, 103, 104, 105],
        status=200
    )
    
    # Act: Call our service
    story_ids = HackerNewsService.fetch_top_stories(limit=3)
    
    # Assert: Verify the result is exactly what we expect (only 3 items)
    assert len(story_ids) == 3
    assert story_ids == [101, 102, 103]

@responses.activate
def test_fetch_story_details():
    # Arrange
    responses.add(
        responses.GET,
        "https://hacker-news.firebaseio.com/v0/item/101.json",
        json={"title": "Why AI is the Future", "url": "https://example.com/ai"},
        status=200
    )
    
    # Act
    story = HackerNewsService.fetch_story_details(101)
    
    # Assert
    assert story['title'] == "Why AI is the Future"
    assert story['url'] == "https://example.com/ai"
