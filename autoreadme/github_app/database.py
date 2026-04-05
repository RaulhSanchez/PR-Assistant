import os
from datetime import datetime, timedelta
from urllib.parse import urlparse

# Support both PostgreSQL (production) and SQLite (local dev)
DATABASE_URL = os.getenv("DATABASE_URL")

def _get_conn():
    if DATABASE_URL:
        import psycopg2
        return psycopg2.connect(DATABASE_URL)
    else:
        import sqlite3
        return sqlite3.connect(os.getenv("DB_PATH", "autoreadme.db"))

def _placeholder():
    """Return the correct placeholder for the active DB driver."""
    return "%s" if DATABASE_URL else "?"

def init_db():
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _placeholder()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS installations (
            installation_id BIGINT PRIMARY KEY,
            repo_count INTEGER DEFAULT 0,
            plan_type TEXT DEFAULT 'free',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_logs (
            id SERIAL PRIMARY KEY,
            installation_id BIGINT,
            event_type TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

def get_or_create_installation(installation_id: int) -> dict:
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _placeholder()
    cursor.execute(
        f"SELECT installation_id, repo_count, plan_type FROM installations WHERE installation_id = {ph}",
        (installation_id,)
    )
    row = cursor.fetchone()
    if not row:
        cursor.execute(
            f"INSERT INTO installations (installation_id) VALUES ({ph})",
            (installation_id,)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"installation_id": installation_id, "repo_count": 0, "plan_type": "free"}
    cursor.close()
    conn.close()
    return {"installation_id": row[0], "repo_count": row[1], "plan_type": row[2]}

def update_repo_count(installation_id: int, count: int):
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _placeholder()
    cursor.execute(
        f"UPDATE installations SET repo_count = {ph} WHERE installation_id = {ph}",
        (count, installation_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

def log_usage(installation_id: int, event_type: str = "pr_analysis"):
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _placeholder()
    cursor.execute(
        f"INSERT INTO usage_logs (installation_id, event_type) VALUES ({ph}, {ph})",
        (installation_id, event_type)
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_monthly_usage(installation_id: int) -> int:
    month_ago = (datetime.now() - timedelta(days=30)).isoformat()
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _placeholder()
    cursor.execute(
        f"SELECT COUNT(*) FROM usage_logs WHERE installation_id = {ph} AND event_type = 'pr_analysis' AND timestamp > {ph}",
        (installation_id, month_ago)
    )
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count

def check_limits(installation_id: int) -> tuple[bool, str]:
    inst = get_or_create_installation(installation_id)
    if inst["plan_type"] == "pro":
        return True, ""

    # Free: max 3 repos
    if int(inst["repo_count"]) > 3:
        return False, "Has alcanzado el límite de 3 repositorios del plan gratuito."

    # Free: max 50 PR analyses/month
    usage = get_monthly_usage(installation_id)
    if usage >= 50:
        return False, "Has alcanzado el límite de 50 análisis de PR mensuales del plan gratuito."

    return True, ""

def upgrade_to_pro(installation_id: int):
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _placeholder()
    cursor.execute(
        f"UPDATE installations SET plan_type = 'pro' WHERE installation_id = {ph}",
        (installation_id,)
    )
    conn.commit()
    cursor.close()
    conn.close()
