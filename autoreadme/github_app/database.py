import sqlite3
from datetime import datetime, timedelta
import os

DB_PATH = os.getenv("DB_PATH", "autoreadme.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Installations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS installations (
                installation_id INTEGER PRIMARY KEY,
                repo_count INTEGER DEFAULT 0,
                plan_type TEXT DEFAULT 'free',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Usage logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                installation_id INTEGER,
                event_type TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (installation_id) REFERENCES installations (installation_id)
            )
        ''')
        conn.commit()

def get_or_create_installation(installation_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT installation_id, repo_count, plan_type FROM installations WHERE installation_id = ?", (installation_id,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("INSERT INTO installations (installation_id) VALUES (?)", (installation_id,))
            conn.commit()
            return {"installation_id": installation_id, "repo_count": 0, "plan_type": "free"}
        return {"installation_id": row[0], "repo_count": row[1], "plan_type": row[2]}

def update_repo_count(installation_id: int, count: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE installations SET repo_count = ? WHERE installation_id = ?", (count, installation_id))
        conn.commit()

def log_usage(installation_id: int, event_type: str = "pr_analysis"):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usage_logs (installation_id, event_type) VALUES (?, ?)", (installation_id, event_type))
        conn.commit()

def get_monthly_usage(installation_id: int):
    month_ago = (datetime.now() - timedelta(days=30)).isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM usage_logs WHERE installation_id = ? AND event_type = 'pr_analysis' AND timestamp > ?",
            (installation_id, month_ago)
        )
        return cursor.fetchone()[0]

def check_limits(installation_id: int) -> tuple[bool, str]:
    inst = get_or_create_installation(installation_id)
    if inst["plan_type"] == "pro":
        return True, ""
    
    # Free limits
    # 1. Repositories limit
    if int(inst["repo_count"]) > 3:
        return False, "Has alcanzado el límite de 3 repositorios para el plan gratuito."
    
    # 2. PRs per month limit
    usage = get_monthly_usage(installation_id)
    if usage >= 50:
        return False, "Has alcanzado el límite de 50 análisis de PR mensuales para el plan gratuito."
    
    return True, ""

if __name__ == "__main__":
    init_db()
