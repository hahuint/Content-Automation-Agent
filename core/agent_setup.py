import os
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from core.config import MODEL_NAME

from tools.wordpress import publish_to_wordpress
from tools.social import broadcast_to_socials
from tools.utilities import calculator, scrape_website, open_website
from tools.research import get_trending_tech_news, get_global_news
from tools.journalist import delegate_to_journalist
from tools.audit import log_activity, read_recent_audit

ollama_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Load Tools
tools = [
    publish_to_wordpress,
    broadcast_to_socials,
    calculator,
    scrape_website,
    open_website,
    get_trending_tech_news,
    get_global_news,
    delegate_to_journalist,
    log_activity,
    read_recent_audit
]

# Initialize LLM
llm = ChatOllama(model=MODEL_NAME, temperature=0, base_url=ollama_url)

# Define System Prompt for the Agent
SYSTEM_PROMPT = """You are the Content Automation Orchestrator. 
Your primary job is to help users manage their content pipeline.

TOOL GUIDELINES:
1. If the user asks to 'visit' or 'open' a site, use 'open_website'.
2. If the user asks for 'news' or 'info' from a site, use 'scrape_website' so you can read it.
3. Often, you should use BOTH: 'open_website' to show the user, and 'scrape_website' to read the content for them.

Always use your tools when asked to perform an action. Be concise and professional.
"""

# Create Agent with System Prompt
agent = create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)
