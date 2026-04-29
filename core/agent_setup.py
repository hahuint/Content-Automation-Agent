import os
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from core.config import MODEL_NAME

from tools.wordpress import publish_to_wordpress
from tools.social import broadcast_to_socials
from tools.utilities import calculator, open_website
from tools.research import get_trending_tech_news, get_global_news
from tools.journalist import delegate_to_journalist
from tools.audit import log_activity, read_recent_audit

ollama_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Initialize LLM
llm = ChatOllama(model=MODEL_NAME, temperature=0.7, base_url=ollama_url)

# Load Tools
tools = [
    publish_to_wordpress,
    broadcast_to_socials,
    calculator,
    open_website,
    get_trending_tech_news,
    get_global_news,
    delegate_to_journalist,
    log_activity,
    read_recent_audit
]

# Create Agent
agent = create_react_agent(llm, tools)
