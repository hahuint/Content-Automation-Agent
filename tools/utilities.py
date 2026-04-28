from langchain_core.tools import tool

@tool
def calculator(expression: str) -> str:
    """Perform basic math calculations."""
    try:
        return str(eval(expression))
    except:
        return "Calculation error."

@tool
def open_website(url: str) -> str:
    """Open any website in your default browser."""
    import webbrowser
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)
    return f"✅ Opened {url}"
