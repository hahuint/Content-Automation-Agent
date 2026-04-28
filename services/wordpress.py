import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from core.config import WP_URL, WP_HEADERS

class WordPressService:
    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def upload_image(image_url: str, filename: str) -> int:
        img_data = requests.get(image_url, timeout=15).content
        headers = {
            'Authorization': WP_HEADERS.get('Authorization', ''),
            'Content-Disposition': f'attachment; filename="{filename}.jpg"',
            'Content-Type': 'image/jpeg'
        }
        response = requests.post(f"{WP_URL}/media", headers=headers, data=img_data)
        response.raise_for_status()
        return response.json()['id']

    @staticmethod
    def create_post(title: str, content: str, media_id: int = None, excerpt: str = None, status: str = "publish"):
        post_data = {
            "title": title,
            "content": content,
            "status": status,
            "format": "standard"
        }
        if media_id:
            post_data["featured_media"] = media_id
        if excerpt:
            post_data["excerpt"] = excerpt
            
        response = requests.post(f"{WP_URL}/posts", headers=WP_HEADERS, json=post_data)
        return response
