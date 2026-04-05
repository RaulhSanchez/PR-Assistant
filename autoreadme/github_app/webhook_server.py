import os
import hmac
import hashlib
import json
import time
import tempfile
import shutil
import subprocess
from typing import Optional

import jwt
import httpx
from fastapi import FastAPI, Request, Header, HTTPException, BackgroundTasks
from pydantic import BaseModel
from contextlib import asynccontextmanager

from ..llm import get_provider
from ..generator import generate_pr_companion_report
from .database import init_db, check_limits, log_usage, update_repo_count, get_or_create_installation

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB
    init_db()
    yield

app = FastAPI(title="autoreadme GitHub App", lifespan=lifespan)

@app.get("/")
@app.get("/health")
def health():
    return {"status": "ok", "app_id": GITHUB_APP_ID}

# Config from env
GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
def _parse_private_key(raw: str) -> str:
    """Normalize the private key regardless of how it was stored in env vars."""
    key = raw.replace("\\n", "\n").strip()
    if not key.startswith("-----BEGIN"):
        key = f"-----BEGIN RSA PRIVATE KEY-----\n{key}\n-----END RSA PRIVATE KEY-----"
    return key

GITHUB_PRIVATE_KEY = _parse_private_key(os.getenv("GITHUB_PRIVATE_KEY", ""))
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")

# LLM Config
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
LLM_MODEL = os.getenv("LLM_MODEL")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

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

async def process_pr(installation_id: int, repo_full_name: str, pr_number: int, base_branch: str, head_branch: str, head_repo_url: str):
    token = await get_installation_token(installation_id)

    # Init LLM
    llm = get_provider(provider=LLM_PROVIDER, model=LLM_MODEL)
    if LLM_PROVIDER == "ollama":
        os.environ["OLLAMA_HOST"] = OLLAMA_BASE_URL

    with tempfile.TemporaryDirectory() as tmpdir:
        # Clone the repo with full history
        clone_url = head_repo_url.replace("https://", f"https://x-access-token:{token}@")
        subprocess.run(["git", "clone", clone_url, tmpdir], check=True, capture_output=True)

        # Fetch all branches so both base and head are available
        subprocess.run(["git", "fetch", "--all"], cwd=tmpdir, check=True, capture_output=True)

        # Checkout the PR's head branch
        subprocess.run(["git", "checkout", head_branch], cwd=tmpdir, check=True, capture_output=True)

        # Generate report — diff is base_branch...HEAD (the PR's head branch)
        report = generate_pr_companion_report(tmpdir, llm, f"origin/{base_branch}")

        # Log usage
        log_usage(installation_id)

        # Post comment to PR
        comment_url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
        }
        async with httpx.AsyncClient() as client:
            await client.post(comment_url, headers=headers, json={"body": report})

@app.post("/webhook")
async def webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: Optional[str] = Header(None)
):
    body = await request.body()
    
    # Verify signature
    if GITHUB_WEBHOOK_SECRET:
        if not x_hub_signature_256:
            raise HTTPException(status_code=401, detail="Missing signature")
        
        sha_name, signature = x_hub_signature_256.split('=')
        if sha_name != 'sha256':
            raise HTTPException(status_code=501, detail="Non-SHA256 signature")
        
        hash_object = hmac.new(GITHUB_WEBHOOK_SECRET.encode(), msg=body, digestmod=hashlib.sha256)
        if not hmac.compare_digest(hash_object.hexdigest(), signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

    payload = json.loads(body)
    event = request.headers.get("X-GitHub-Event")

    if event == "installation":
        action = payload.get("action")
        installation_id = payload["installation"]["id"]
        if action in ["created", "new_permissions_accepted"]:
            # On creation, we ensure the installation exists in DB
            get_or_create_installation(installation_id)
        return {"status": "ok"}

    if event == "installation_repositories":
        action = payload.get("action")
        installation_id = payload["installation"]["id"]
        # In a real app we'd query GitHub to get the exact current count
        # For now, let's assume we just need to ensure the record exists
        get_or_create_installation(installation_id)
        return {"status": "ok"}

    if event == "pull_request":
        action = payload.get("action")
        if action in ["opened", "synchronize"]:
            installation_id = payload["installation"]["id"]
            
            # CHECK LIMITS
            allowed, reason = check_limits(installation_id)
            if not allowed:
                # Post a "Limit reached" comment instead of analyzing
                repo_full_name = payload["repository"]["full_name"]
                pr_number = payload["pull_request"]["number"]
                background_tasks.add_task(post_limit_reached_comment, installation_id, repo_full_name, pr_number, reason)
                return {"status": "limit_reached", "reason": reason}

            repo_full_name = payload["repository"]["full_name"]
            pr_number = payload["pull_request"]["number"]
            base_branch = payload["pull_request"]["base"]["ref"]
            head_branch = payload["pull_request"]["head"]["ref"]
            head_repo_url = payload["pull_request"]["head"]["repo"]["clone_url"]

            background_tasks.add_task(
                process_pr,
                installation_id,
                repo_full_name,
                pr_number,
                base_branch,
                head_branch,
                head_repo_url,
            )
            return {"status": "processing"}

    return {"status": "ignored"}

async def post_limit_reached_comment(installation_id: int, repo_full_name: str, pr_number: int, reason: str):
    token = await get_installation_token(installation_id)
    comment_url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    body = f"### ⚠️ Límite de Plan Gratuito Alcanzado\n\n{reason}\n\nPara seguir disfrutando de PR-Assistant sin límites, considera actualizar a nuestro plan Pro."
    async with httpx.AsyncClient() as client:
        await client.post(comment_url, headers=headers, json={"body": body})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
