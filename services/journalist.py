import requests
import re
from google import genai
from core.config import GROK_API_KEY, GEMINI_API_KEY, GEMINI_MODEL, SITE_NAME

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
        
        prompt = f"""You are an elite journalist for {SITE_NAME}. Write a highly engaging, 4-paragraph news article based on the facts below.
        
        You MUST respond in pure JSON format matching exactly this schema.
        {{
            "title": "A catchy, SEO-friendly news title",
            "content": "The 4 paragraph HTML content (use <p>, <h2>, <strong> where appropriate)",
            "image_search_term": "A 1-2 word search term for a stock photo (e.g. 'technology', 'africa')",
            "tags": "3 comma-separated SEO tags",
            "seo_meta_description": "A 150-character SEO meta description"
        }}
        
        Topic: {topic}
        Raw Facts: {raw_facts}
        """
        
        from core.config import GROK_MODEL
        data = {
            "model": GROK_MODEL,
            "messages": [
                {"role": "system", "content": "You are a professional journalist. Respond ONLY with raw JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            content = response.json()["choices"][0]["message"]["content"].strip()
            
            # Robust JSON Extraction
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json_match.group(0)
            
            return content
            
        except Exception as e:
            print(f"⚠️ Grok API failed: {str(e)}. Attempting Gemini fallback ({GEMINI_MODEL})...")
            if not GEMINI_API_KEY:
                return f"Error: Grok failed and no Gemini API key configured: {str(e)}"
            
            try:
                client = genai.Client(api_key=GEMINI_API_KEY)
                gemini_prompt = f"{prompt}\n\nIMPORTANT: Respond ONLY with the raw JSON object."
                
                response = client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=gemini_prompt
                )
                
                content = str(response.text).strip()
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json_match.group(0)
                return content
            except Exception as gemini_e:
                return f"Error: Both Grok and Gemini failed. Grok: {str(e)} | Gemini: {str(gemini_e)}"
