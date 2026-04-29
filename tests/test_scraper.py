from tools.utilities import scrape_website

def test_scrape_website_valid():
    """Test scraping a known valid website (example.com)."""
    result = scrape_website.invoke({"url": "https://example.com"})
    assert "Example Domain" in result
    assert "Error" not in result

def test_scrape_website_invalid():
    """Test scraping a non-existent URL."""
    result = scrape_website.invoke({"url": "https://this-website-does-not-exist-12345.com"})
    assert "Error" in result

def test_scrape_website_formatting():
    """Test that the scraper removes HTML tags and returns clean text."""
    result = scrape_website.invoke({"url": "https://example.com"})
    assert "<html>" not in result
    assert "<script>" not in result
    assert len(result) > 0
