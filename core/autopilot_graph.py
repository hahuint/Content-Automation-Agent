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
    recent = state.get('recent_topics', [])
    
    # Try multiple category fallbacks
    categories = ["trending", "global", "africa"]
    chosen = None
    news = None
    
    def select_topic(news_content):
        """Select a unique topic from available news."""
        if not news_content or len(news_content.strip()) < 50:
            print(f"  [DEBUG] News content too short or empty: {len(news_content) if news_content else 0} chars")
            return "NONE_AVAILABLE"
            
        prompt = f"""
        TASK: Select a UNIQUE news topic for a new article.
        CRITICAL RESTRICTION: You MUST NOT select any topic that has been covered before.
        RECENTLY PUBLISHED TOPICS (DO NOT REPEAT THESE):
        {recent if recent else 'None yet - all topics are available'}
        AVAILABLE NEWS HEADLINES:
        {news_content}
        INSTRUCTIONS:
        1. Compare the available headlines against the 'RECENTLY PUBLISHED TOPICS' list.
        2. If a headline is similar to an existing topic, DISCARD IT.
        3. Select the most interesting REMAINING topic.
        4. IF ALL HEADLINES ARE ALREADY IN THE LIST, YOU MUST RETURN THE EXACT STRING 'NONE_AVAILABLE'.
        Return ONLY the chosen topic or 'NONE_AVAILABLE'. Do not explain your reasoning.
        """
        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            result = str(response.content).strip().split('\n')[0]
            print(f"  [DEBUG] LLM returned: {result[:80]}")
            return result
        except Exception as e:
            print(f"  [DEBUG] LLM Error: {e}")
            return "NONE_AVAILABLE"

    # Try categories in order until we get a valid topic
    for category in categories:
        print(f"Selecting topic from '{category}' news...")
        try:
            news = get_global_news.invoke({"category": category})
            print(f"  [DEBUG] News length: {len(news) if news else 0} chars")
            
            if not news:
                print(f"  [DEBUG] No news returned for {category}")
                continue
                
            chosen = select_topic(news)
            print(f"  [DEBUG] Topic selection result: {chosen[:80] if chosen else 'None'}")
            
            if chosen and "NONE_AVAILABLE" not in chosen.upper():
                # Verify not a duplicate
                is_duplicate = any(
                    r.lower()[:50] in chosen.lower() or chosen.lower()[:50] in r.lower() 
                    for r in recent
                )
                if not is_duplicate:
                    print(f"✅ Selected Topic: {chosen}")
                    return {"raw_news": news, "best_topic": chosen}
                else:
                    print(f"  [DEBUG] Topic is duplicate, trying next category")
            else:
                print(f"  [DEBUG] LLM returned NONE_AVAILABLE, trying next category")
        except Exception as e:
            print(f"  [DEBUG] Error fetching {category} news: {e}")
            continue
    
    # If all categories exhausted, skip this cycle
    print("⚠️ No new topics available across all categories. Skipping this cycle.")
    return {"best_topic": "NONE", "raw_news": "NONE"}

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

def publish_node(state: AutoPilotState):
    """
    Unified Distribution Node: Handles both Social Media Broadcasting and WordPress CMS Publishing.
    """
    if state.get("best_topic") == "NONE" or state.get("composed_json") == "Error":
        return {"published_url": "Skipped", "broadcast_status": "Skipped"}

    print("🚀 Initiating Distribution Phase...")
    
    # 1. Publish to WordPress
    print("☁️ Publishing to WordPress CMS...")
    published_url = "Error"
    try:
        data = json.loads(state["composed_json"])
        published_url = publish_to_wordpress.invoke({
            "title": data["title"],
            "content": data["content"],
            "image_search_term": data["image_search_term"],
            "comma_separated_tags": data["tags"],
            "seo_meta_description": data["seo_meta_description"]
        })
    except Exception as e:
        print(f"❌ WordPress Error: {e}")
        published_url = f"Error: {e}"

    # 2. Broadcast to Social Channels
    print("📢 Broadcasting to Social Channels...")
    broadcast_status = "Error"
    try:
        broadcast_status = broadcast_to_socials.invoke({
            "topic": state["best_topic"],
            "url": published_url if not published_url.startswith("Error") else "Direct Update"
        })
        if "telegram" in broadcast_status.lower() and "success" in broadcast_status.lower():
            print("📢 Telegram: done")
        if "x_twitter" in broadcast_status.lower() and "success" in broadcast_status.lower():
            print("📢 X (Twitter): done")
    except Exception as e:
        print(f"❌ Broadcast Error: {e}")
        broadcast_status = f"Error: {e}"

    return {"published_url": published_url, "broadcast_status": broadcast_status}

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
workflow.add_node("publish", publish_node)
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
        "continue": "publish",
        "revise": "draft"
    }
)

workflow.add_edge("publish", "log")
workflow.add_edge("log", END)

workflow.set_entry_point("audit")
autopilot_app = workflow.compile()
