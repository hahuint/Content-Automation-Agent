import requests
from core.config import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
    X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET
)

class SocialDistributionService:
    """
    A generic, omnichannel broadcasting service. 
    It safely checks if credentials exist in .env before attempting to post to an API.
    """
    
    @staticmethod
    def broadcast_all(message: str, url: str) -> dict:
        results = {}
        
        # 1. Telegram Integration
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            results["telegram"] = SocialDistributionService.post_to_telegram(message, url)
        else:
            results["telegram"] = "Skipped (No TELEGRAM_BOT_TOKEN)"
            
        # 2. X (Twitter) Integration
        if X_API_KEY and X_API_SECRET and X_ACCESS_TOKEN and X_ACCESS_SECRET:
            results["x_twitter"] = SocialDistributionService.post_to_x(message, url)
        else:
            results["x_twitter"] = "Skipped (No X API credentials)"
        
        return results

    @staticmethod
    def post_to_telegram(message: str, url: str) -> str:
        text = f"📰 <b>{message}</b>\n\n🔗 Read the full article here:\n{url}"
        api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        }
        
        try:
            response = requests.post(api_url, json=payload, timeout=15)
            response.raise_for_status()
            return "Success"
        except Exception as e:
            return f"Failed: {str(e)}"

    @staticmethod
    def post_to_x(message: str, url: str) -> str:
        """Posts to X (Twitter) using OAuth 1.0a User Context."""
        try:
            from requests_oauthlib import OAuth1
            
            auth = OAuth1(X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET)
            text = f"📰 {message}\n\nFull story: {url}"
            
            # X API v2 Endpoint for Tweets
            endpoint = "https://api.twitter.com/2/tweets"
            payload = {"text": text}
            
            response = requests.post(endpoint, auth=auth, json=payload, timeout=15)
            response.raise_for_status()
            return "Success"
        except ImportError:
            return "Failed: requests-oauthlib not installed"
        except Exception as e:
            return f"Failed: {str(e)}"

