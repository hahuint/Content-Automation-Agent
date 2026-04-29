import json
from typing import TypedDict, List
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from core.agent_setup import llm
from tools.research import get_global_news
from tools.journalist import delegate_to_journalist
from tools.social import broadcast_to_socials
from tools.wordpress import publish_to_wordpress
from tools.audit import log_activity, read_recent_audit, read_recent_topics

# 1. Define State
class AutoPilotState(TypedDict):
    recent_posts: str
    recent_topics: List[str]
    raw_news: str
    best_topic: str
    composed_json: str
    broadcast_status: str
    published_url: str
    status: str
    # New state for the Self-Correction Loop
    draft_feedback: str
    iteration_count: int

# 2. Define Nodes
def check_audit_node(state: AutoPilotState):
    print("Checking publication history...")
    return {
        "recent_posts": read_recent_audit.invoke({}),
        "recent_topics": read_recent_topics.invoke({}),
        "iteration_count": 0,
        "draft_feedback": ""
    }

def research_node(state: AutoPilotState):
    print("Fetching latest news feeds...")
    news = get_global_news.invoke({"category": "trending"})
    
    print("Selecting topic...")
    recent = state.get('recent_topics', [])
    
    def select_topic(news_content):
        prompt = f"""
        TASK: Select a UNIQUE news topic for a new article.
        CRITICAL RESTRICTION: You MUST NOT select any topic that has been covered before.
        RECENTLY PUBLISHED TOPICS (DO NOT REPEAT THESE):
        {recent}
        AVAILABLE NEWS HEADLINES:
        {news_content}
        INSTRUCTIONS:
        1. Compare the available headlines against the 'RECENTLY PUBLISHED TOPICS' list.
        2. If a headline is similar to an existing topic, DISCARD IT.
        3. Select the most interesting REMAINING topic.
        4. IF ALL HEADLINES ARE ALREADY IN THE LIST, YOU MUST RETURN THE EXACT STRING 'NONE_AVAILABLE'.
        Return ONLY the chosen topic or 'NONE_AVAILABLE'. Do not explain your reasoning.
        """
        response = llm.invoke([HumanMessage(content=prompt)])
        return str(response.content).strip().split('\n')[0]

    chosen = select_topic(news)
    
    # Fallback to World news if Trending is exhausted
    if "NONE_AVAILABLE" in chosen.upper() or any(r.lower()[:50] in chosen.lower() or chosen.lower()[:50] in r.lower() for r in recent):
        print("⚠️ Trending news exhausted. Falling back to 'World' category...")
        news = get_global_news.invoke({"category": "world"})
        chosen = select_topic(news)

    # Final duplication check
    is_duplicate = any(r.lower()[:50] in chosen.lower() or chosen.lower()[:50] in r.lower() for r in recent)
    if is_duplicate or "NONE_AVAILABLE" in chosen.upper():
        print(f"🛑 Duplicate Protection: Skipping topic '{chosen}'.")
        return {"best_topic": "NONE", "raw_news": "NONE"}

    print(f"Selected Topic: {chosen}")
    return {"raw_news": news, "best_topic": chosen}

def draft_node(state: AutoPilotState):
    if state.get("best_topic") == "NONE":
        return {"composed_json": "Error"}
        
    iteration = state.get("iteration_count", 0) + 1
    feedback = state.get("draft_feedback", "")
    
    print(f"Drafting content (Attempt {iteration}) for: {state['best_topic']}")
    
    context = f"Topic: {state['best_topic']}\nRaw Facts: {state['raw_news']}"
    if feedback:
        context += f"\n\nPREVIOUS FEEDBACK FROM EDITOR: {feedback}\nPlease rewrite the article addressing these specific points."

    composed_json = delegate_to_journalist.invoke({"topic": state["best_topic"], "raw_facts": context})
    
    if not composed_json.strip().startswith("{"):
        return {"composed_json": "Error"}

    return {"composed_json": composed_json, "iteration_count": iteration}

def editor_node(state: AutoPilotState):
    """
    Self-Correction Node: Evaluates the draft and provides feedback for improvement.
    """
    if state.get("best_topic") == "NONE" or state.get("composed_json") == "Error":
        return {"draft_feedback": "Skip"}

    print("🧐 Editor critiquing draft...")
    draft = state["composed_json"]
    
    prompt = f"""
    You are the Chief Editor for a premium news bureau. Evaluate the following news draft for:
    1. Quality & Tone: Is it professional and engaging?
    2. SEO: Are the tags and meta description effective?
    3. Formatting: Is the HTML clean and well-structured?
    
    DRAFT:
    {draft}
    
    INSTRUCTIONS:
    - If the draft is excellent (8/10 or higher), return the string 'APPROVED'.
    - If it needs improvement, return a concise list of 2-3 specific improvements needed.
    
    Return ONLY 'APPROVED' or your feedback list.
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    feedback = str(response.content).strip()
    
    if "APPROVED" in feedback.upper() or state.get("iteration_count", 0) >= 2:
        print("✅ Editor: Approved for publication.")
        return {"draft_feedback": "APPROVED"}
    
    print(f"📝 Editor Feedback: {feedback}")
    return {"draft_feedback": feedback}

def broadcast_node(state: AutoPilotState):
    if state.get("best_topic") == "NONE" or state.get("composed_json") == "Error":
        return {"broadcast_status": "Skipped"}

    print("Broadcasting to social channels...")
    url = state.get("published_url", "") or "Direct Update (No Link)"
        
    result_str = broadcast_to_socials.invoke({
        "topic": state["best_topic"],
        "url": url
    })
    
    if "telegram" in result_str.lower() and "success" in result_str.lower():
        print("📢 Telegram: done")
    if "x_twitter" in result_str.lower() and "success" in result_str.lower():
        print("📢 X (Twitter): done")
    
    return {"broadcast_status": result_str}

def cms_node(state: AutoPilotState):
    if state.get("best_topic") == "NONE" or state.get("composed_json") == "Error":
        return {"published_url": "Skipped"}

    print("Publishing to WordPress...")
    try:
        data = json.loads(state["composed_json"])
        url = publish_to_wordpress.invoke({
            "title": data["title"],
            "content": data["content"],
            "image_search_term": data["image_search_term"],
            "comma_separated_tags": data["tags"],
            "seo_meta_description": data["seo_meta_description"]
        })
        return {"published_url": url}
    except Exception as e:
        print(f"❌ Error in CMS node: {e}")
        return {"published_url": f"Error: {e}"}

def log_node(state: AutoPilotState):
    if state.get("best_topic") == "NONE":
        return {"status": "Complete (Skipped)"}
        
    print("Logging activity...")
    log_activity.invoke({
        "action": "Automated Content Publish & Broadcast",
        "status": "Success",
        "topic": state["best_topic"],
        "url": state.get("published_url", "N/A")
    })
    return {"status": "Complete"}

# 3. Build the Loop-Aware Graph
workflow = StateGraph(AutoPilotState)

workflow.add_node("audit", check_audit_node)
workflow.add_node("research", research_node)
workflow.add_node("draft", draft_node)
workflow.add_node("editor", editor_node)
workflow.add_node("broadcast", broadcast_node)
workflow.add_node("cms", cms_node)
workflow.add_node("log", log_node)

workflow.add_edge("audit", "research")
workflow.add_edge("research", "draft")
workflow.add_edge("draft", "editor")

# The Self-Correction Loop Logic
def should_continue(state: AutoPilotState):
    if state.get("draft_feedback") == "APPROVED" or state.get("draft_feedback") == "Skip":
        return "continue"
    return "revise"

workflow.add_conditional_edges(
    "editor",
    should_continue,
    {
        "continue": "broadcast",
        "revise": "draft"
    }
)

workflow.add_edge("broadcast", "cms")
workflow.add_edge("cms", "log")
workflow.add_edge("log", END)

workflow.set_entry_point("audit")
autopilot_app = workflow.compile()
