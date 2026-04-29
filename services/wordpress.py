import requests
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from core.config import WP_URL, WP_HEADERS

class WordPressService:
    # Use a persistent session to avoid SSL EOF errors
    _session = requests.Session()
    if WP_HEADERS:
        _session.headers.update(WP_HEADERS)

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def upload_media(img_url: str):
        img_data = requests.get(img_url, timeout=20).content
        headers = {
            'Content-Disposition': 'attachment; filename="featured_image.jpg"',
            'Content-Type': 'image/jpeg'
        }
        response = WordPressService._session.post(f"{WP_URL}/media", headers=headers, data=img_data, timeout=30)
        response.raise_for_status()
        return response.json()['id']

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def create_post(title: str, content: str, media_id: Optional[int] = None, excerpt: str = "", status: str = "publish"):
        post_data: Dict[str, Any] = {
            "title": title,
            "content": content,
            "status": status,
            "format": "standard"
        }
        if media_id:
            post_data["featured_media"] = media_id
        if excerpt:
            post_data["excerpt"] = excerpt
            
        response = WordPressService._session.post(f"{WP_URL}/posts", json=post_data, timeout=30)
        response.raise_for_status()
        return response
