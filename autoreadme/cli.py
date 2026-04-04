"""
autoreadme CLI — AI-powered PR Companion & README Generator.
"""
from __future__ import annotations

import json
import os
import sys
import time

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table

console = Console()

CONFIG_DIR = os.path.expanduser("~/.autoreadme")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

PROVIDERS = ["ollama", "openai", "anthropic", "gemini"]


# ── Config helpers ────────────────────────────────────────────────────────────

def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"provider": "ollama", "model": None, "api_keys": {}}


def save_config(cfg: dict) -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


# ── CLI root ──────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--provider", "-p", default=None, type=click.Choice(PROVIDERS))
@click.option("--model", "-m", default=None)
def cli(ctx, provider, model):
    """AI-powered README Generator and PR Companion."""
    if ctx.invoked_subcommand is None:
        # Default behavior: run 'analyze' on current directory
        ctx.invoke(analyze, project_path=".", provider=provider, model=model)


@cli.command("analyze")
@click.argument("project_path", default=".", required=False)
@click.option("--provider", "-p", default=None, type=click.Choice(PROVIDERS))
@click.option("--model", "-m", default=None)
@click.option("--output", "-o", default=None, help="Output path for README.md")
@click.option("--workers", "-w", default=4, type=int)
@click.option("--no-routes", is_flag=True, default=False)
@click.option("--cache-dir", default="/tmp/autoreadme_cache")
def analyze(project_path, provider, model, output, workers, no_routes, cache_dir):
    """Generate a professional README for your project."""
    cfg = load_config()
    provider = provider or cfg.get("provider", "ollama")
    model = model or cfg.get("model")
    api_key = cfg.get("api_keys", {}).get(provider)

    project_path = os.path.abspath(project_path)
    if not os.path.isdir(project_path):
        console.print(f"[red]Error:[/red] '{project_path}' is not a directory.")
        sys.exit(1)

    output_path = output or os.path.join(project_path, "README.md")

    console.print(Panel.fit(
        f"[bold cyan]autoreadme - Analyze[/bold cyan]\n"
        f"Project: [white]{project_path}[/white]\n"
        f"Provider: [green]{provider}[/green]  "
        f"Model: [yellow]{model or 'default'}[/yellow]\n"
        f"Output: [blue]{output_path}[/blue]",
        border_style="cyan",
    ))

    # Init LLM
    try:
        from .llm import get_provider as _get_provider
        llm = _get_provider(provider=provider, model=model, api_key=api_key)
        console.print(f"[green]✓[/green] LLM provider ready: {provider} / {llm.model}")
    except Exception as e:
        console.print(f"[red]✗ Failed to init LLM:[/red] {e}")
        sys.exit(1)

    # Analyze
    from .analyzer import analyze_project
    start_time = time.time()
    processed_files = [0]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        scan_task = progress.add_task("[cyan]Analyzing project...", total=None)

        def progress_callback(processed, total, filepath, elapsed, remaining):
            processed_files[0] = processed
            progress.update(scan_task, total=total, completed=processed,
                             description=f"[cyan]Analyzing ({processed}/{total}) {os.path.basename(filepath)}")

        project_data = analyze_project(
            project_path=project_path,
            llm=llm,
            workers=workers,
            cache_dir=cache_dir,
            progress_callback=progress_callback,
        )

    # Language summary
    if project_data.language_summary:
        table = Table(title="Languages Detected", show_header=True, header_style="bold cyan")
        table.add_column("Language")
        table.add_column("Files", justify="right")
        for lang, count in sorted(project_data.language_summary.items(), key=lambda x: -x[1]):
            table.add_row(lang, str(count))
        console.print(table)

    # Generate README
    console.print("\n[cyan]⚙[/cyan]  Generating README...")
    from .generator import generate_readme
    generate_readme(data=project_data, output_path=output_path, llm=llm, enrich_routes=not no_routes)

    total_time = time.time() - start_time
    console.print(Panel.fit(f"[bold green]✅ README generated![/bold green] ({total_time:.1f}s)", border_style="green"))


@cli.command("pr")
@click.argument("project_path", default=".", required=False)
@click.option("--base", "-b", default="main", help="Base branch for diff.")
@click.option("--provider", "-p", default=None, type=click.Choice(PROVIDERS))
@click.option("--model", "-m", default=None)
def cli_pr(project_path, base, provider, model):
    """AI-powered PR Companion: Summary, Breaking Changes & Tests."""
    cfg = load_config()
    provider = provider or cfg.get("provider", "ollama")
    model = model or cfg.get("model")
    api_key = cfg.get("api_keys", {}).get(provider)
    
    from .llm import get_provider as _get_provider
    llm = _get_provider(provider=provider, model=model, api_key=api_key)
    
    project_path = os.path.abspath(project_path)
    
    console.print(Panel.fit(
        f"[bold cyan]PR Companion[/bold cyan]\n"
        f"Project: [white]{project_path}[/white]\n"
        f"Base: [yellow]{base}[/yellow]  Provider: [green]{provider}[/green]",
        border_style="cyan",
    ))
    
    from .generator import generate_pr_companion_report
    try:
        report = generate_pr_companion_report(project_path, llm, base)
        console.print(Panel(report, border_style="green", title="AI Report"))
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@cli.group()
def config():
    """Manage autoreadme configuration."""
    pass

@config.command("show")
def config_show():
    """Show current configuration."""
    cfg = load_config()
    table = Table(title="autoreadme config", show_header=True, header_style="bold cyan")
    table.add_column("Key")
    table.add_column("Value")
    table.add_row("Default provider", cfg.get("provider", "ollama"))
    table.add_row("Default model", cfg.get("model") or "(default)")
    console.print(table)

@config.command("set-provider")
@click.argument("provider", type=click.Choice(PROVIDERS))
def config_set_provider(provider):
    cfg = load_config()
    cfg["provider"] = provider
    save_config(cfg)
    console.print(f"[green]✓[/green] Default provider: [bold]{provider}[/bold]")

@config.command("set-key")
@click.argument("provider", type=click.Choice(PROVIDERS))
@click.argument("api_key")
def config_set_key(provider, api_key):
    cfg = load_config()
    cfg.setdefault("api_keys", {})[provider] = api_key
    save_config(cfg)
    console.print(f"[green]✓[/green] API key for {provider} saved.")
