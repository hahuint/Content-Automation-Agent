import os
from dotenv import load_dotenv
import base64

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", "llama3.2:3b")

# WordPress Settings
WP_URL = os.getenv("WP_URL")
SITE_NAME = os.getenv("SITE_NAME", "YourBlogName")
WP_USERNAME = os.getenv("WP_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
GROK_API_KEY = os.getenv("GROK_API_KEY", "")

# Social Media API Keys
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# WordPress Auth Header
if WP_USERNAME and WP_APP_PASSWORD:
    wp_credentials = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
    WP_TOKEN = base64.b64encode(wp_credentials.encode()).decode('utf-8')
    WP_HEADERS = {'Authorization': f'Basic {WP_TOKEN}'}
else:
    WP_TOKEN = ""
    WP_HEADERS = {}
