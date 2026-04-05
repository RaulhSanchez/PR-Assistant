import os
import hmac
import hashlib
import json
import time
import tempfile
import subprocess
from typing import Optional
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlparse, quote

import jwt
import httpx
import stripe
from fastapi import FastAPI, Request, Header, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from ..llm import get_provider
from ..generator import generate_pr_companion_report
from .database import (
    init_db, check_limits, log_usage, update_repo_count, 
    get_or_create_installation, upgrade_to_pro, add_pending_pro, 
    check_and_activate_pro, is_paid, get_installation_by_org
)

# ── Config ──────────────────────────────────────────────────────────────────

GITHUB_APP_ID        = os.getenv("GITHUB_APP_ID")
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")
LLM_PROVIDER         = os.getenv("LLM_PROVIDER", "gemini")
LLM_MODEL            = os.getenv("LLM_MODEL")
OLLAMA_BASE_URL      = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
STRIPE_API_KEY       = os.getenv("STRIPE_API_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
STRIPE_PRICE_ID      = os.getenv("STRIPE_PRICE_ID")
BASE_URL             = os.getenv("BASE_URL", "http://localhost:8000")
GITHUB_APP_NAME      = os.getenv("GITHUB_APP_NAME", "repo-docs-ai")

stripe.api_key = STRIPE_API_KEY

def _parse_private_key(raw: str) -> str:
    key = raw.replace("\\n", "\n").strip()
    if not key.startswith("-----BEGIN"):
        key = f"-----BEGIN RSA PRIVATE KEY-----\n{key}\n-----END RSA PRIVATE KEY-----"
    return key

GITHUB_PRIVATE_KEY = _parse_private_key(os.getenv("GITHUB_PRIVATE_KEY", ""))

# ── App ──────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="PR-Assistant GitHub App", lifespan=lifespan)

# CORS es necesario para que el navegador permita las llamadas del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── HTML pages ───────────────────────────────────────────────────────────────

def _read_html(name: str) -> str:
    path = Path(__file__).parent / name
    return path.read_text()

@app.get("/", response_class=HTMLResponse)
def landing():
    # Buscamos index.html en la raíz del proyecto para servir la interfaz
    root_dir = Path(__file__).parent.parent.parent
    index_path = root_dir / "index.html"
    if index_path.exists():
        return index_path.read_text()
    return HTMLResponse("<h1>index.html no encontrado</h1>", status_code=404)

@app.get("/health")
def health():
    return {"status": "ok", "app_id": GITHUB_APP_ID}

@app.get("/success", response_class=HTMLResponse)
def success():
    return _read_html("success.html")

@app.get("/cancel", response_class=HTMLResponse)
def cancel():
    return _read_html("cancel.html")

# ── GitHub JWT ───────────────────────────────────────────────────────────────

def get_jwt() -> str:
    payload = {
        "iat": int(time.time()) - 60,
        "exp": int(time.time()) + (10 * 60),
        "iss": GITHUB_APP_ID,
    }
    return jwt.encode(payload, GITHUB_PRIVATE_KEY, algorithm="RS256")

async def get_installation_token(installation_id: int) -> str:
    token_jwt = get_jwt()
    headers = {
        "Authorization": f"Bearer {token_jwt}",
        "Accept": "application/vnd.github+json",
    }
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers)
        resp.raise_for_status()
        return resp.json()["token"]

# ── PR processing ────────────────────────────────────────────────────────────

async def process_pr(installation_id: int, repo_full_name: str, pr_number: int,
                     base_branch: str, head_branch: str, head_repo_url: str):
    token = await get_installation_token(installation_id)
    llm = get_provider(provider=LLM_PROVIDER, model=LLM_MODEL)
    if LLM_PROVIDER == "ollama":
        os.environ["OLLAMA_HOST"] = OLLAMA_BASE_URL

    with tempfile.TemporaryDirectory() as tmpdir:
        clone_url = head_repo_url.replace("https://", f"https://x-access-token:{token}@")
        subprocess.run(["git", "clone", clone_url, tmpdir], check=True, capture_output=True)
        subprocess.run(["git", "fetch", "--all"], cwd=tmpdir, check=True, capture_output=True)
        subprocess.run(["git", "checkout", head_branch], cwd=tmpdir, check=True, capture_output=True)
        report = generate_pr_companion_report(tmpdir, llm, f"origin/{base_branch}")

    log_usage(installation_id)

    comment_url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    async with httpx.AsyncClient() as client:
        await client.post(comment_url, headers=headers, json={"body": report})

async def post_limit_reached_comment(installation_id: int, repo_full_name: str,
                                      pr_number: int, reason: str):
    token = await get_installation_token(installation_id)
    comment_url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    checkout_url = f"{BASE_URL}/create-checkout-session?installation_id={installation_id}"
    body = (
        f"### ⚠️ PR-Assistant — Free Plan Limit Reached\n\n"
        f"{reason}\n\n"
        f"[**Upgrade to Pro →**]({checkout_url}) — Unlimited repos & analyses for $12/month."
    )
    async with httpx.AsyncClient() as client:
        await client.post(comment_url, headers=headers, json={"body": body})

# ── GitHub Webhook ───────────────────────────────────────────────────────────

@app.post("/webhook")
async def webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: Optional[str] = Header(None),
):
    body = await request.body()

    if GITHUB_WEBHOOK_SECRET:
        if not x_hub_signature_256:
            raise HTTPException(status_code=401, detail="Missing signature")
        sha_name, signature = x_hub_signature_256.split("=")
        if sha_name != "sha256":
            raise HTTPException(status_code=501, detail="Non-SHA256 signature")
        mac = hmac.new(GITHUB_WEBHOOK_SECRET.encode(), msg=body, digestmod=hashlib.sha256)
        if not hmac.compare_digest(mac.hexdigest(), signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

    payload = json.loads(body)
    event = request.headers.get("X-GitHub-Event")

    # Track new installations
    if event == "installation":
        installation_id = payload["installation"]["id"]
        org_name = payload["installation"]["account"]["login"]
        repos_added = payload.get("repositories", [])
        
        # This will create the installation record if it doesn't exist
        get_or_create_installation(installation_id)
        
        # Check if they paid BEFORE installing
        # This ALSO updates the org_name in the installations table
        check_and_activate_pro(installation_id, org_name)

        if repos_added:
            update_repo_count(installation_id, len(repos_added))
        return {"status": "ok"}

    # Track repo additions/removals
    if event == "installation_repositories":
        installation_id = payload["installation"]["id"]
        inst = get_or_create_installation(installation_id)
        added = len(payload.get("repositories_added", []))
        removed = len(payload.get("repositories_removed", []))
        new_count = max(0, inst["repo_count"] + added - removed)
        update_repo_count(installation_id, new_count)
        return {"status": "ok"}

    if event == "pull_request":
        action = payload.get("action")
        if action in ["opened", "synchronize"]:
            installation_id = payload["installation"]["id"]
            allowed, reason = check_limits(installation_id)
            repo_full_name = payload["repository"]["full_name"]
            pr_number = payload["pull_request"]["number"]

            if not allowed:
                background_tasks.add_task(
                    post_limit_reached_comment,
                    installation_id, repo_full_name, pr_number, reason
                )
                return {"status": "limit_reached"}

            base_branch = payload["pull_request"]["base"]["ref"]
            head_branch = payload["pull_request"]["head"]["ref"]
            head_repo_url = payload["pull_request"]["head"]["repo"]["clone_url"]
            background_tasks.add_task(
                process_pr,
                installation_id, repo_full_name, pr_number,
                base_branch, head_branch, head_repo_url,
            )
            return {"status": "processing"}

    return {"status": "ignored"}

@app.get("/check-payment")
async def check_payment(org: str):
    """Check if an org/username has already paid for Pro."""
    if is_paid(org):
        return {"paid": True}
    return {"paid": False}

# ── Stripe ───────────────────────────────────────────────────────────────────

@app.get("/checkout")
async def checkout_by_org(org: str):
    """Redirect directly to Stripe checkout using the provided GitHub org/username."""
    if not STRIPE_API_KEY or not STRIPE_PRICE_ID:
        raise HTTPException(status_code=503, detail="Payments not configured yet")
    
    # We no longer check if installed. We just go to Stripe.
    return RedirectResponse(
        url=f"/create-checkout-session?org_name={quote(org)}", 
        status_code=302
    )

@app.get("/create-checkout-session")
async def create_checkout_session(org_name: str):
    if not STRIPE_API_KEY or not STRIPE_PRICE_ID:
        raise HTTPException(status_code=503, detail="Payments not configured")
    try:
        session = stripe.checkout.Session.create(
            line_items=[{"price": STRIPE_PRICE_ID, "quantity": 1}],
            mode="subscription",
            success_url=f"https://github.com/apps/{GITHUB_APP_NAME}/installations/new",
            cancel_url=f"{BASE_URL}/cancel",
            metadata={"org_name": org_name},
        )
        return RedirectResponse(url=session.url, status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        org_name = session.get("metadata", {}).get("org_name")
        if org_name:
            # Try to upgrade immediately if already installed
            installation_id = get_installation_by_org(org_name)
            if installation_id:
                upgrade_to_pro(installation_id)
                print(f"🚀 Existing installation {installation_id} upgraded to Pro for {org_name}")
            else:
                add_pending_pro(org_name)
                print(f"💰 Purchase completed for {org_name}. Pending installation.")

    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
