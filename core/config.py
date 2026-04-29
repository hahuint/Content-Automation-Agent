import os
from dotenv import load_dotenv
import base64

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", "llama3.2:3b")
GROK_MODEL = os.getenv("GROK_MODEL", "grok-4-1-fast-non-reasoning")

# WordPress Settings
WP_URL = os.getenv("WP_URL")
SITE_NAME = os.getenv("SITE_NAME", "YourBlogName")
WP_USERNAME = os.getenv("WP_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
GROK_API_KEY = os.getenv("GROK_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Social Media API Keys
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
X_API_KEY = os.getenv("X_API_KEY", "")
X_API_SECRET = os.getenv("X_API_SECRET", "")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN", "")
X_ACCESS_SECRET = os.getenv("X_ACCESS_SECRET", "")

# WordPress Auth Header
if WP_USERNAME and WP_APP_PASSWORD:
    wp_credentials = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
    WP_TOKEN = base64.b64encode(wp_credentials.encode()).decode('utf-8')
    WP_HEADERS = {
        'Authorization': f'Basic {WP_TOKEN}',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
else:
    WP_TOKEN = ""
    WP_HEADERS = {}
