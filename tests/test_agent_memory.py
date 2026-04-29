import requests
import pytest

print("DEBUG: test_agent_memory.py is being read")

def test_simple_check():
    assert True

def test_agent_audit_memory():
    # Detect if Ollama is online
    try:
        from core.agent_setup import ollama_url
        requests.get(ollama_url, timeout=1)
    except Exception:
        pytest.skip("Ollama is not running")

    from core.agent_setup import agent
    from services.audit import AuditService
    from core.config import WP_URL
    
    # Parse the base URL from the WP_URL setting
    base_url = WP_URL.replace("/wp-json/wp/v2", "") if WP_URL else "https://example.com"

    AuditService.log_action(
        topic="The Future of Autonomous AI", 
        action="Published blog post and broadcast to social media", 
        status="Success", 
        url=f"{base_url}/future-ai"
    )
    
    print("\n🤖 Asking the Agent: 'What did you do today?'")
    response = agent.invoke({"messages": [("human", "What did you do today? Check your audit logs and give me a report.")]})
    
    assert "The Future of Autonomous AI" in response['messages'][-1].content
    assert "publish" in response['messages'][-1].content.lower()
