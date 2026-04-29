import sqlite3

DB_PATH = "agent_audit.db"

class AuditService:
    @staticmethod
    def _get_connection():
        conn = sqlite3.connect(DB_PATH)
        # Create table if it doesn't exist
        conn.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                topic TEXT,
                action TEXT,
                status TEXT,
                url TEXT
            )
        ''')
        return conn

    @staticmethod
    def log_action(topic: str, action: str, status: str, url: str = ""):
        conn = AuditService._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO audit_logs (topic, action, status, url)
            VALUES (?, ?, ?, ?)
        ''', (topic, action, status, url))
        conn.commit()
        conn.close()
        return "Action logged successfully."

    @staticmethod
    def get_recent_topics(limit: int = 20):
        """Returns a simple list of topics to help orchestrator avoid duplicates."""
        conn = AuditService._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT topic FROM audit_logs ORDER BY timestamp DESC LIMIT ?', (limit,))
        topics = [row[0] for row in cursor.fetchall()]
        conn.close()
        return topics

    @staticmethod
    def get_recent_logs(limit: int = 10):
        conn = AuditService._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, topic, action, status, url 
            FROM audit_logs 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return "No recent logs found in the database."
            
        report = ["=== RECENT AUDIT LOGS ==="]
        for row in rows:
            report.append(f"[{row[0]}] {row[2]} | Topic: '{row[1]}' | Status: {row[3]} | URL: {row[4]}")
        return "\n".join(report)
