import requests
from core.config import GROK_API_KEY

class JournalistService:
    @staticmethod
    def write_article(topic: str, raw_facts: str) -> str:
        if not GROK_API_KEY:
            return "Error: GROK_API_KEY is not configured."
            
        print(f"✍️ [The Journalist] Grok is writing the article about '{topic}'... (Please wait)")
        
        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        from core.config import SITE_NAME
        prompt = f"""You are an elite journalist for {SITE_NAME}. Write a highly engaging, 3-paragraph news article based on the facts below.
        
        You MUST respond in pure JSON format matching exactly this schema. Do NOT wrap it in markdown codeblocks.
        {{
            "title": "A catchy, SEO-friendly news title",
            "content": "The 3 paragraph HTML content (use <p>, <h2>, <strong> where appropriate)",
            "image_search_term": "A 1-2 word search term for a stock photo (e.g. 'technology', 'africa')",
            "tags": "3 comma-separated SEO tags",
            "seo_meta_description": "A 150-character SEO meta description"
        }}
        
        Topic: {topic}
        Raw Facts/News:
        {raw_facts}
        """
        
        data = {
            "model": "grok-2-latest",
            "messages": [
                {"role": "system", "content": "You are a professional journalist. Respond ONLY with raw JSON. No conversational text."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "response_format": {"type": "json_object"}
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            content = response.json()["choices"][0]["message"]["content"].strip()
            
            # Clean up markdown if Grok disobeys
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
                
            return content.strip()
            
        except Exception as e:
            return f"❌ Error from Grok API: {str(e)}"
