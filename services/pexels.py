import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from core.config import PEXELS_API_KEY

class PexelsService:
    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_image_url(query: str) -> str:
        if not PEXELS_API_KEY:
            return None
            
        url = f"https://api.pexels.com/v1/search?query={query}&per_page=1&orientation=landscape"
        headers = {"Authorization": PEXELS_API_KEY}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data.get('photos') and len(data['photos']) > 0:
            # Get the high quality landscape version of the image
            return data['photos'][0]['src']['landscape']
            
        return None
