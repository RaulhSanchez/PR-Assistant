"""
pr_handler.py — Orchestrates the full PR analysis pipeline.

Called by the webhook server when a PR event arrives.
"""
from __future__ import annotations

import os

from ..differ import analyze_changes
from ..generator import build_pr_report
from ..llm import get_provider
from .github_client import GitHubClient


def handle_pr_event(
    owner: str,
    repo: str,
    pr_number: int,
    pr_title: str,
    pr_url: str,
    base_sha: str,
    client: GitHubClient,
) -> str:
    """
    Full pipeline: fetch PR data → run analysis → post comment.

    Returns the generated report markdown.
    """
    # ── 1. Fetch diff ─────────────────────────────────────────────────────
    diff = client.get_pr_diff(owner, repo, pr_number)
    changed_files = client.get_pr_files(owner, repo, pr_number)

    # ── 2. AST breaking change detection ─────────────────────────────────
    breaking_changes: list[str] = []
    for file_info in changed_files:
        fp = file_info.get("filename", "")
        if not fp.endswith(".py"):
            continue  # AST diff only for Python for now

        new_content = client.get_file_content(owner, repo, fp, ref="HEAD")
        old_content = client.get_file_content(owner, repo, fp, ref=base_sha)

        if new_content and old_content:
            report = analyze_changes(fp, old_content, new_content)
            if report.is_breaking:
                for bc in report.signature_changes:
                    breaking_changes.append(f"Firma cambiada: `{fp}` → {bc}")
                for func in report.removed_functions:
                    breaking_changes.append(f"Función eliminada: `{fp}` → `{func}()`")

    # ── 3. Init LLM ───────────────────────────────────────────────────────
    provider = os.environ.get("LLM_PROVIDER", "openai")
    model = os.environ.get("LLM_MODEL") or None
    api_key = os.environ.get("LLM_API_KEY") or None
    llm = get_provider(provider=provider, model=model, api_key=api_key)

    # ── 4. Generate report ────────────────────────────────────────────────
    report_md = build_pr_report(
        diff=diff,
        llm=llm,
        breaking_changes=breaking_changes,
        pr_title=pr_title,
        pr_url=pr_url,
    )

    # ── 5. Post/update comment on the PR ─────────────────────────────────
    client.upsert_comment(owner, repo, pr_number, report_md)

    return report_md
