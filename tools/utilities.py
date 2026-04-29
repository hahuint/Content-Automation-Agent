from langchain_core.tools import tool

@tool
def calculator(expression: str) -> str:
    """Perform basic math calculations."""
    try:
        return str(eval(expression))
    except Exception:
        return "Calculation error."

@tool
def open_website(url: str) -> str:
    """Open any website in the USER'S default browser for visual inspection."""
    import webbrowser
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)
    return f"✅ Opened {url} in your browser."

@tool
def scrape_website(url: str) -> str:
    """Read the actual text content of any website URL."""
    import requests
    from bs4 import BeautifulSoup
    
    if not url.startswith("http"):
        url = "https://" + url
        
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Newsroom Agent)"}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        text = soup.get_text()
        # Break into lines and remove leading/trailing whitespace
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return clean_text[:2000] # Return first 2000 chars to avoid token blowup
    except Exception as e:
        return f"Error reading website: {str(e)}"
