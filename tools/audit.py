from langchain_core.tools import tool
from services.audit import AuditService

@tool
def log_activity(topic: str, action: str, status: str, url: str = "") -> str:
    """
    Log an action you just completed to the database.
    Use this immediately after you publish a post or perform a major task.
    Status should be 'Success' or 'Failed'.
    """
    return AuditService.log_action(topic, action, status, url)

@tool
def read_recent_audit() -> str:
    """
    Read the recent audit logs to see what you did today or recently.
    Use this to see past actions, avoid duplicating topics, or when the user asks what you did.
    """
    return AuditService.get_recent_logs(10)
