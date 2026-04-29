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
    print("Drafting content with Journalist...")
    from tools.journalist import delegate_to_journalist
    import json
    
    # 1. Compose the content
    composed_json = delegate_to_journalist.invoke({"topic": state["best_topic"], "raw_facts": state["raw_news"]})
    
    try:
        data = json.loads(composed_json)
        
        # 2. Dynamic Publishing (Plug and Play)
        # We check the .env config inside the tool or here
        from tools.wordpress import publish_to_wordpress
        from core.config import WP_URL
        
        if WP_URL:
            print("Publishing to WordPress...")
            url = publish_to_wordpress.invoke({
                "title": data["title"],
                "content": data["content"],
                "image_search_term": data["image_search_term"],
                "comma_separated_tags": data["tags"],
                "seo_meta_description": data["seo_meta_description"]
            })
            return {"published_url": url}
        else:
            print("No WordPress URL configured. Skipping CMS upload.")
            return {"published_url": "No CMS configured"}
            
    except Exception as e:
        print(f"❌ Error in publishing node: {e}")
        return {"published_url": f"Error: {e}"}


def broadcast_node(state: AutoPilotState):
    print("Broadcasting to social channels...")
    from tools.social import broadcast_to_socials
    # Pass the topic and the returned URL to the generic broadcaster
    if "http" in str(state.get("published_url", "")):
        broadcast_to_socials.invoke({"topic": state["best_topic"], "url": state["published_url"]})
    return {} # State doesn't need updating here

def log_node(state: AutoPilotState):
    print("Logging activity...")
    from tools.audit import log_activity
    log_activity.invoke({
        "action": "Automated Content Publish & Broadcast",
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
workflow.add_node("broadcast", broadcast_node)
workflow.add_node("log", log_node)

workflow.add_edge("audit", "research")
workflow.add_edge("research", "publish")
workflow.add_edge("publish", "broadcast")
workflow.add_edge("broadcast", "log")
workflow.add_edge("log", END)

workflow.set_entry_point("audit")
autopilot_app = workflow.compile()
