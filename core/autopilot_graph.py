from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from core.agent_setup import llm

# 1. Define the State
class AutoPilotState(TypedDict):
    recent_posts: str
    raw_news: str
    best_topic: str
    published_url: str
    status: str

# 2. Define Nodes (The steps)
def check_audit_node(state: AutoPilotState):
    print("Checking publication history...")
    from tools.audit import read_recent_audit
    return {"recent_posts": read_recent_audit.invoke({})}

def research_node(state: AutoPilotState):
    print("Fetching latest news feeds...")
    from tools.research import get_global_news
    news = get_global_news.invoke({"category": "global"})
    
    print("Selecting topic...")
    # Using Llama to select the best topic
    prompt = f"""
    Review these news headlines:
    {news}
    
    Review the recent posts we already made so we don't duplicate:
    {state.get('recent_posts', 'None')}
    
    Select the single most interesting news topic from the list that we haven't covered yet.
    Return ONLY a 1-sentence description of the chosen topic. Do not explain your reasoning.
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    chosen = response.content.strip()
    
    print(f"Selected Topic: {chosen}")
    return {"raw_news": news, "best_topic": chosen}

def publish_node(state: AutoPilotState):
    print("Drafting and publishing article...")
    from tools.journalist import delegate_to_journalist
    result = delegate_to_journalist.invoke({"topic": state["best_topic"], "raw_facts": state["raw_news"]})
    return {"published_url": result}

def log_node(state: AutoPilotState):
    print("Logging activity...")
    from tools.audit import log_activity
    log_activity.invoke({
        "action": "Automated Content Publish",
        "status": "Success",
        "topic": state["best_topic"],
        "url": state["published_url"]
    })
    return {"status": "Complete"}

# 3. Build the Future-Proof Graph
workflow = StateGraph(AutoPilotState)

workflow.add_node("audit", check_audit_node)
workflow.add_node("research", research_node)
workflow.add_node("publish", publish_node)
workflow.add_node("log", log_node)

workflow.add_edge("audit", "research")
workflow.add_edge("research", "publish")
workflow.add_edge("publish", "log")
workflow.add_edge("log", END)

workflow.set_entry_point("audit")
autopilot_app = workflow.compile()
