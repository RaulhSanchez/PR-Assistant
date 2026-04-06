import os
from datetime import datetime, timedelta
from urllib.parse import urlparse
from typing import Optional

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
            org_name TEXT,
            repo_count INTEGER DEFAULT 0,
            plan_type TEXT DEFAULT 'free',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pending_pro_activations (
            org_name TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_logs (
            id BIGSERIAL PRIMARY KEY,
            installation_id BIGINT NOT NULL,
            event_type TEXT DEFAULT 'pr_analysis',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Migrations: add columns that may be missing in older deployments
    for migration in [
        "ALTER TABLE installations ADD COLUMN IF NOT EXISTS org_name TEXT",
        "ALTER TABLE installations ADD COLUMN IF NOT EXISTS repo_count INTEGER DEFAULT 0",
        "ALTER TABLE installations ADD COLUMN IF NOT EXISTS plan_type TEXT DEFAULT 'free'",
    ]:
        try:
            cursor.execute(migration)
        except Exception:
            pass
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

def add_pending_pro(org_name: str):
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _placeholder()
    cursor.execute(
        f"INSERT INTO pending_pro_activations (org_name) VALUES ({ph})",
        (org_name,)
    )
    conn.commit()
    cursor.close()
    conn.close()

def is_paid(org_name: str) -> bool:
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _placeholder()
    # Check if they have an installation that is Pro
    cursor.execute(
        f"SELECT 1 FROM installations WHERE org_name = {ph} AND plan_type = 'pro'",
        (org_name,)
    )
    if cursor.fetchone():
        return True
    # Check if they have a pending activation
    cursor.execute(
        f"SELECT 1 FROM pending_pro_activations WHERE org_name = {ph}",
        (org_name,)
    )
    res = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return res

def check_and_activate_pro(installation_id: int, org_name: str) -> bool:
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _placeholder()
    # Always save the org name for future lookups
    cursor.execute(
        f"UPDATE installations SET org_name = {ph} WHERE installation_id = {ph}",
        (org_name, installation_id)
    )
    
    cursor.execute(
        f"SELECT 1 FROM pending_pro_activations WHERE org_name = {ph}",
        (org_name,)
    )
    if cursor.fetchone():
        upgrade_to_pro(installation_id)
        cursor.execute(
            f"DELETE FROM pending_pro_activations WHERE org_name = {ph}",
            (org_name,)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    conn.commit()
    cursor.close()
    conn.close()
    return False

def get_installation_by_org(org_name: str) -> Optional[int]:
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _placeholder()
    cursor.execute(
        f"SELECT installation_id FROM installations WHERE org_name = {ph}",
        (org_name,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None

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

def downgrade_to_free_by_org(org_name: str):
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _placeholder()
    cursor.execute(
        f"UPDATE installations SET plan_type = 'free' WHERE org_name = {ph}",
        (org_name,)
    )
    # Also remove from pending if they cancel before installing
    cursor.execute(
        f"DELETE FROM pending_pro_activations WHERE org_name = {ph}",
        (org_name,)
    )
    conn.commit()
    cursor.close()
    conn.close()
