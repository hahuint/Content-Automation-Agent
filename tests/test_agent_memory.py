from services.audit import AuditService
from core.agent_setup import agent
from core.config import WP_URL

print("📝 Injecting a test entry into the Audit Database...")

# Parse the base URL from the WP_URL setting
base_url = WP_URL.replace("/wp-json/wp/v2", "") if WP_URL else "https://example.com"

AuditService.log_action(
    topic="The Future of Autonomous AI", 
    action="Published blog post and broadcast to social media", 
    status="Success", 
    url=f"{base_url}/future-ai"
)
print("✅ Entry saved!")

print("\n🤖 Asking the Agent: 'What did you do today?'")
response = agent.invoke({"messages": [("human", "What did you do today? Check your audit logs and give me a report.")]})

print("\n=== AGENT'S REPORT ===")
print(response['messages'][-1].content)
