"""
github_client.py — GitHub API client for the autoreadme GitHub App.

Handles:
- Authentication via JWT (App) and installation tokens
- Fetching PR diffs
- Posting/updating PR comments
"""
from __future__ import annotations

import time
import httpx
import jwt  # PyJWT


class GitHubClient:
    """Authenticated GitHub API client for a specific installation."""

    BASE_URL = "https://api.github.com"

    def __init__(self, app_id: str, private_key: str, installation_id: int):
        self.app_id = app_id
        self.private_key = private_key
        self.installation_id = installation_id
        self._token: str | None = None
        self._token_expires_at: float = 0

    # ── Authentication ────────────────────────────────────────────────────

    def _make_jwt(self) -> str:
        """Generate a short-lived JWT to authenticate as the GitHub App."""
        now = int(time.time())
        payload = {
            "iat": now - 60,   # issued 60s ago to allow clock drift
            "exp": now + 540,  # expires in 9 minutes (max 10)
            "iss": self.app_id,
        }
        return jwt.encode(payload, self.private_key, algorithm="RS256")

    def _get_installation_token(self) -> str:
        """Exchange the JWT for a short-lived installation access token."""
        if self._token and time.time() < self._token_expires_at - 60:
            return self._token

        app_jwt = self._make_jwt()
        response = httpx.post(
            f"{self.BASE_URL}/app/installations/{self.installation_id}/access_tokens",
            headers={
                "Authorization": f"Bearer {app_jwt}",
                "Accept": "application/vnd.github+json",
            },
        )
        response.raise_for_status()
        data = response.json()
        self._token = data["token"]
        # Tokens expire after 1 hour
        self._token_expires_at = time.time() + 3600
        return self._token

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._get_installation_token()}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    # ── PR data ───────────────────────────────────────────────────────────

    def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """Fetch the full diff of a pull request."""
        response = httpx.get(
            f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}",
            headers={**self._headers(), "Accept": "application/vnd.github.diff"},
            timeout=30,
        )
        response.raise_for_status()
        return response.text

    def get_pr_info(self, owner: str, repo: str, pr_number: int) -> dict:
        """Fetch PR metadata (title, body, author, base branch, etc.)."""
        response = httpx.get(
            f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}",
            headers=self._headers(),
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

    def get_pr_files(self, owner: str, repo: str, pr_number: int) -> list[dict]:
        """Fetch the list of changed files in a PR."""
        response = httpx.get(
            f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}/files",
            headers=self._headers(),
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

    def get_file_content(self, owner: str, repo: str, path: str, ref: str) -> str | None:
        """Fetch the content of a file at a specific git ref (for AST diffing)."""
        import base64
        response = httpx.get(
            f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}",
            headers=self._headers(),
            params={"ref": ref},
            timeout=15,
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()
        if data.get("encoding") == "base64":
            return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        return None

    # ── PR comments ───────────────────────────────────────────────────────

    def find_bot_comment(self, owner: str, repo: str, pr_number: int) -> int | None:
        """Find an existing autoreadme comment on the PR to update instead of creating a new one."""
        response = httpx.get(
            f"{self.BASE_URL}/repos/{owner}/{repo}/issues/{pr_number}/comments",
            headers=self._headers(),
            timeout=15,
        )
        response.raise_for_status()
        for comment in response.json():
            if "autoreadme — PR Companion" in comment.get("body", ""):
                return comment["id"]
        return None

    def post_comment(self, owner: str, repo: str, pr_number: int, body: str) -> dict:
        """Post a new comment on a PR."""
        response = httpx.post(
            f"{self.BASE_URL}/repos/{owner}/{repo}/issues/{pr_number}/comments",
            headers=self._headers(),
            json={"body": body},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

    def update_comment(self, owner: str, repo: str, comment_id: int, body: str) -> dict:
        """Update an existing PR comment."""
        response = httpx.patch(
            f"{self.BASE_URL}/repos/{owner}/{repo}/issues/comments/{comment_id}",
            headers=self._headers(),
            json={"body": body},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

    def upsert_comment(self, owner: str, repo: str, pr_number: int, body: str) -> dict:
        """Post a new comment or update the existing autoreadme comment."""
        comment_id = self.find_bot_comment(owner, repo, pr_number)
        if comment_id:
            return self.update_comment(owner, repo, comment_id, body)
        return self.post_comment(owner, repo, pr_number, body)
