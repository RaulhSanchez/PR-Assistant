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
    check_and_activate_pro, is_paid, get_installation_by_org,
    downgrade_to_free_by_org,
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

# Validate required secrets at startup
_missing = [v for v in ["GITHUB_APP_ID", "GITHUB_PRIVATE_KEY", "GITHUB_WEBHOOK_SECRET"] if not os.getenv(v)]
if _missing:
    raise RuntimeError(f"Missing required environment variables: {', '.join(_missing)}")

# ── App ──────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="PR-Assistant GitHub App", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://github.com",
        "https://raulhsanchez.github.io",
        BASE_URL,
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
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

async def post_error_comment(token: str, repo_full_name: str, pr_number: int, message: str):
    comment_url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
    body = f"### ⚠️ PR-Assistant — Analysis failed\n\n{message}\n\n_This is usually a temporary issue. It will retry on your next push._"
    async with httpx.AsyncClient() as client:
        await client.post(comment_url, headers=headers, json={"body": body})

async def process_pr(installation_id: int, repo_full_name: str, pr_number: int,
                     base_branch: str, head_branch: str, head_repo_url: str):
    try:
        token = await get_installation_token(installation_id)
    except Exception as e:
        print(f"[process_pr] Failed to get installation token: {e}")
        return

    try:
        llm = get_provider(provider=LLM_PROVIDER, model=LLM_MODEL)
        if LLM_PROVIDER == "ollama":
            os.environ["OLLAMA_HOST"] = OLLAMA_BASE_URL
    except Exception as e:
        print(f"[process_pr] Failed to init LLM provider: {e}")
        await post_error_comment(token, repo_full_name, pr_number, "Could not initialize AI provider.")
        return

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            clone_url = head_repo_url.replace("https://", f"https://x-access-token:{token}@")
            subprocess.run(["git", "clone", "--depth=50", clone_url, tmpdir],
                           check=True, capture_output=True, timeout=120)
            subprocess.run(["git", "fetch", "--all"], cwd=tmpdir,
                           check=True, capture_output=True, timeout=60)
            subprocess.run(["git", "checkout", head_branch], cwd=tmpdir,
                           check=True, capture_output=True, timeout=30)
            report = generate_pr_companion_report(tmpdir, llm, f"origin/{base_branch}")
    except subprocess.CalledProcessError as e:
        err = e.stderr.decode(errors="ignore") if e.stderr else str(e)
        print(f"[process_pr] Git error: {err}")
        await post_error_comment(token, repo_full_name, pr_number, "Could not clone or checkout the repository.")
        return
    except subprocess.TimeoutExpired:
        print(f"[process_pr] Git operation timed out for {repo_full_name}")
        await post_error_comment(token, repo_full_name, pr_number, "Repository clone timed out.")
        return
    except Exception as e:
        print(f"[process_pr] Analysis error: {e}")
        await post_error_comment(token, repo_full_name, pr_number, "AI analysis failed. Please try again.")
        return

    log_usage(installation_id)

    try:
        comment_url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
        async with httpx.AsyncClient() as client:
            await client.post(comment_url, headers=headers, json={"body": report})
    except Exception as e:
        print(f"[process_pr] Failed to post comment: {e}")

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

    # If they've already paid, send them straight to GitHub installation
    if is_paid(org):
        return RedirectResponse(
            url=f"https://github.com/apps/{GITHUB_APP_NAME}/installations/new",
            status_code=302,
        )

    return RedirectResponse(
        url=f"/create-checkout-session?org_name={quote(org)}",
        status_code=302,
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
            installation_id = get_installation_by_org(org_name)
            if installation_id:
                upgrade_to_pro(installation_id)
                print(f"🚀 Installation {installation_id} upgraded to Pro for {org_name}")
            else:
                add_pending_pro(org_name)
                print(f"💰 Purchase completed for {org_name}. Pending installation.")

    elif event["type"] in ("customer.subscription.deleted", "customer.subscription.updated"):
        sub = event["data"]["object"]
        # Only downgrade if subscription is actually cancelled/incomplete
        status = sub.get("status", "")
        if status in ("canceled", "incomplete_expired", "unpaid"):
            org_name = sub.get("metadata", {}).get("org_name")
            if org_name:
                downgrade_to_free_by_org(org_name)
                print(f"⬇️ {org_name} downgraded to Free (subscription {status})")

    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
